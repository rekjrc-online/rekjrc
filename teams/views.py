from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views import View
from django.views.generic import ListView, DeleteView
from profiles.models import Profile
from .models import Team
from .forms import TeamForm

class TeamListView(LoginRequiredMixin, ListView):
    model = Team
    template_name = 'teams/team_list.html'
    context_object_name = 'teams'

    def get_queryset(self):
        return Team.objects.filter(profile__human=self.request.user).select_related('profile').order_by('profile__displayname')

class TeamBuildView(View):
    template_name = 'teams/team_build.html'

    def get(self, request, profile_uuid):
        profile = get_object_or_404(Profile, uuid=profile_uuid)
        if profile.human != request.user:
            return redirect('teams:team_list')

        team, created = Team.objects.get_or_create(profile=profile)
        form = TeamForm(instance=team)
        return render(request, self.template_name, {'profile': profile, 'form': form})

    def post(self, request, profile_uuid):
        profile = get_object_or_404(Profile, uuid=profile_uuid)
        if profile.human != request.user:
            return redirect('profiles:detail-profile', profile_uuid)

        team, created = Team.objects.get_or_create(profile=profile)
        form = TeamForm(request.POST, instance=team)
        if form.is_valid():
            team = form.save(commit=False)
            team.profile = profile
            team.save()
            return redirect('profiles:detail-profile', profile_uuid)

        return render(request, self.template_name, {'profile': profile, 'form': form})

class TeamDeleteView(DeleteView):
    model = Team
    template_name = 'teams/team_confirm_delete.html'
    success_url = reverse_lazy('teams:team_list')

    def get_object(self):
        profile_uuid = self.kwargs.get('profile_uuid')
        profile = get_object_or_404(Profile, uuid=profile_uuid)
        team = get_object_or_404(Team, profile=profile)
        if profile.human != self.request.user:
            return redirect('profiles:detail-profile', profile_uuid)
        return team
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse, reverse_lazy
from django.views import View
from django.views.generic import ListView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin

from profiles.models import Profile
from .models import Club
from .forms import ClubForm

class ClubListView(LoginRequiredMixin, ListView):
    model = Club
    template_name = 'clubs/club_list.html'
    context_object_name = 'clubs'
    login_url = '/humans/login/'

    def get_queryset(self):
        return (
            Club.objects
            .filter(profile__human=self.request.user)
            .select_related('profile')
            .order_by('id')
        )

class ProfileMixin:
    def setup(self, request, *args, **kwargs):
        super().setup(request, *args, **kwargs)
        self.profile = get_object_or_404(
            Profile,
            uuid=self.kwargs['profile_uuid'],
            human=self.request.user
        )
        return None

class ClubBuildView(LoginRequiredMixin, ProfileMixin, View):
    template_name = 'clubs/club_build.html'
    login_url = '/humans/login/'

    def get(self, request, profile_uuid):
        # If a club exists for this profile, redirect to update page
        existing = Club.objects.filter(profile=self.profile).first()
        if existing:
            return redirect('clubs:club_update', profile_uuid=self.profile.id)

        return render(request, self.template_name, {
            'profile': self.profile,
            'form': ClubForm(),
        })

    def post(self, request, profile_uuid):
        # Ownership already guaranteed by ProfileMixin
        form = ClubForm(request.POST)

        if form.is_valid():
            club = form.save(commit=False)
            club.profile = self.profile
            club.save()
            return redirect('clubs:club_detail', profile_uuid=self.profile.id)

        return render(request, self.template_name, {
            'profile': self.profile,
            'form': form,
        })

class ClubDeleteView(LoginRequiredMixin, ProfileMixin, DeleteView):
    model = Club
    template_name = 'clubs/club_confirm_delete.html'
    login_url = '/humans/login/'

    def dispatch(self, request, *args, **kwargs):
        self.club = get_object_or_404(
            Club,
            profile=self.profile
        )
        return super().dispatch(request, *args, **kwargs)

    def get_object(self, queryset=None):
        return self.club

    def get_success_url(self):
        return reverse_lazy('clubs:club_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['profile'] = self.profile
        return context

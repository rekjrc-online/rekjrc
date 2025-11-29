from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views import View
from django.views.generic import ListView, DeleteView
from profiles.models import Profile
from .models import Track
from .forms import TrackForm, TrackAttributeFormSet

class TrackListView(LoginRequiredMixin, ListView):
    model = Track
    template_name = 'tracks/track_list.html'
    context_object_name = 'tracks'

    def get_queryset(self):
        return Track.objects.filter(profile__human=self.request.user).select_related('profile').order_by('profile__displayname')

class TrackBuildView(View):
    template_name = 'tracks/track_build.html'

    def get(self, request, profile_uuid):
        profile = get_object_or_404(Profile, uuid=profile_uuid)
        if profile.human != request.user:
            return redirect('profiles:detail-profile', profile_uuid=profile.id)
        existing_track = Track.objects.filter(profile=profile).first()
        if existing_track:
            return redirect('profiles:detail-profile', profile_uuid=profile.id)
        form = TrackForm(initial={'human': profile.human, 'profile': profile})
        return render(request, self.template_name, {'profile': profile, 'form': form})

    def post(self, request, profile_uuid):
        profile = get_object_or_404(Profile, uuid=profile_uuid)
        if profile.human != request.user:
            return redirect('profiles:detail-profile', profile_uuid=profile.id)
        form = TrackForm(request.POST, initial={'human': profile.human, 'profile': profile})
        if form.is_valid():
            track = form.save(commit=False)
            track.human = profile.human
            track.profile = profile
            track.save()
            return redirect('profiles:detail-profile', profile_uuid=profile.id)
        return render(request, self.template_name, {'profile': profile, 'form': form})

class TrackDeleteView(DeleteView):
    model = Track
    template_name = 'tracks/track_confirm_delete.html'

    def get_object(self):
        profile_uuid = self.kwargs['profile_uuid']
        profile = get_object_or_404(Profile, uuid=profile_uuid)
        if profile.human != self.request.user:
            return redirect('profiles:detail-profile', profile_uuid=profile.id)
        return get_object_or_404(Track, profile=profile)

    def get_success_url(self):
        profile_uuid = self.kwargs['profile_uuid']
        return reverse('profiles:detail-profile', kwargs={'profile_uuid': profile_uuid})

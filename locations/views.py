from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, DeleteView
from profiles.models import Profile
from .models import Location
from .forms import LocationForm

class LocationListView(LoginRequiredMixin, ListView):
    model = Location
    template_name = 'locations/location_list.html'
    context_object_name = 'locations'
    login_url = '/humans/login/'

    def get_queryset(self):
        return (
            Location.objects
            .filter(profile__human=self.request.user)
            .select_related('profile')
            .order_by('profile__displayname'))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        unused_location_profiles = (
            Profile.objects
            .filter(
                human=self.request.user,
                profiletype='LOCATION',
                locations__isnull=True
            ).order_by('displayname'))

        context['unused_location_profiles'] = unused_location_profiles
        return context

class ProfileMixin:
    def setup(self, request, *args, **kwargs):
        super().setup(request, *args, **kwargs)
        self.profile = get_object_or_404(Profile,id=self.kwargs['profile_uuid'],human=self.request.user)
        return None

class LocationBuildView(LoginRequiredMixin, ProfileMixin, CreateView):
    model = Location
    form_class = LocationForm
    template_name = 'locations/location_form.html'
    login_url = '/humans/login/'

    def dispatch(self, request, *args, **kwargs):
        # If the location already exists, redirect to update view
        if Location.objects.filter(profile=self.profile).exists():
            return redirect('locations:location_update', profile_uuid=self.profile.uuid)

        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['profile'] = self.profile
        context['is_update'] = False
        return context

    def form_valid(self, form):
        form.instance.profile = self.profile
        form.instance.human = self.request.user  # Human *is* the Django user
        self.object = form.save()
        return redirect('locations:location_detail', profile_uuid=self.profile.uuid)

class LocationDeleteView(LoginRequiredMixin, ProfileMixin, DeleteView):
    model = Location
    template_name = 'locations/location_confirm_delete.html'
    login_url = '/humans/login/'

    def dispatch(self, request, *args, **kwargs):
        # Ensure the location exists AND belongs to this profile
        self.location = get_object_or_404(Location, profile=self.profile)
        return super().dispatch(request, *args, **kwargs)

    def get_object(self, queryset=None):
        return self.location

    def get_success_url(self):
        return reverse_lazy('locations:location_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['profile'] = self.profile
        return context

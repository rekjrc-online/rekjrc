from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, DeleteView, View
from profiles.models import Profile
from .models import Event, EventInterest
from .forms import EventForm

class EventListView(LoginRequiredMixin, ListView):
    model = Event
    template_name = 'events/event_list.html'
    context_object_name = 'events'
    login_url = '/humans/login/'
    def get_queryset(self):
        return Event.objects.filter(profile__human=self.request.user).select_related('profile', 'location').order_by('-eventdate')

class EventBuildView(LoginRequiredMixin, CreateView):
    model = Event
    form_class = EventForm
    template_name = 'events/event_build.html'
    login_url = '/humans/login/'

    def dispatch(self, request, *args, **kwargs):
        profile = get_object_or_404(Profile, uuid=self.kwargs['profile_uuid'], human=self.request.user)
        if not profile:
            return redirect('profiles:detail-profile', profile.uuid)

        if Event.objects.filter(profile=profile).exists():
            return redirect('profiles:update-profile', profile_uuid=profile.uuid)
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        profile = get_object_or_404(Profile, uuid=self.kwargs['profile_uuid'], human=self.request.user)
        form.instance.profile = profile
        form.save()
        return redirect('profiles:detail-profile', profile_uuid=profile.uuid)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['profile'] = get_object_or_404(Profile, uuid=self.kwargs['profile_uuid'], human=self.request.user)
        return context

class EventDeleteView(LoginRequiredMixin, DeleteView):
    model = Event
    template_name = 'events/event_confirm_delete.html'
    login_url = '/humans/login/'

    def get_object(self):
        event = get_object_or_404(Event, uuid=self.kwargs['event_id'], human=self.request.user)
        if not event:
            return redirect('profiles:detail-profile', uuid=self.kwargs['profile_uuid'])
        return event

    def get_success_url(self):
        return reverse_lazy('events:event_list')

    def get(self, request, *args, **kwargs):
        profile = get_object_or_404(Profile, uuid=self.kwargs['profile_uuid'], human=self.request.user)
        if not profile:
            return redirect('profiles:detail-profile', profile.uuid)
        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['profile'] = get_object_or_404(Profile, uuid=self.kwargs['profile_uuid'], human=self.request.user)
        return context

class AddInterestView(LoginRequiredMixin, View):
    login_url = '/humans/login/'
    def post(self, request, event_id):
        event = get_object_or_404(Event, uuid=event_id)
        EventInterest.objects.get_or_create(event=event, human=request.user)
        return redirect('events:event_detail', event_id=event_id)

class RemoveInterestView(LoginRequiredMixin, View):
    login_url = '/humans/login/'
    def post(self, request, event_id):
        event = get_object_or_404(Event, uuid=event_id)
        EventInterest.objects.filter(event=event, human=request.user).delete()
        return redirect('events:event_detail', event_id=event_id)

from django import forms
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect, reverse, get_object_or_404, render
from django.views.generic import DetailView, ListView, CreateView, DeleteView, View
from django.conf import settings
from .forms import ProfileEditForm, ProfileCreateForm
from .models import Profile

from builds.models import Build
from builds.forms import BuildForm, BuildAttributeFormSet
from clubs.models import Club
from clubs.forms import ClubForm, ClubLocationFormSet
from events.models import Event
from events.forms import EventForm
from locations.models import Location
from locations.forms import LocationForm
from races.models import Race
from races.forms import RaceForm, RaceAttributeFormSet
from stores.models import Store
from stores.forms import StoreForm
from teams.models import Team
from teams.forms import TeamForm
from tracks.models import Track
from tracks.forms import TrackForm, TrackAttributeFormSet

import os
import qrcode
import logging
logger = logging.getLogger(__name__)

class ProfileUpdateView(LoginRequiredMixin, View):
    template_name = 'profiles/profile_update.html'
    related_models = {
        'model': {
            'model': Build,
            'form': BuildForm,
            'subforms': {
                'attributes': {
                    'fk': 'build',
                    'formset': BuildAttributeFormSet}}},
        'club': {
            'model': Club,
            'form': ClubForm,
            'subforms': {
                'locations': {
                    'fk': 'club',
                    'formset': ClubLocationFormSet}}},
        'race': {
            'model': Race,
            'form': RaceForm,
            'subforms': {
                'attributes': {
                    'fk': 'race',
                    'formset': RaceAttributeFormSet}}},
        'track': {
            'model': Track,
            'form': TrackForm,
            'subforms': {
                'attributes': {
                    'fk': 'track',
                    'formset': TrackAttributeFormSet}}},
        'event': {'model': Event, 'form': EventForm},
        'location': {'model': Location, 'form': LocationForm},
        'store': {'model': Store, 'form': StoreForm},
        'team': {'model': Team, 'form': TeamForm},
    }

    def get(self, request, profile_uuid):
        profile = get_object_or_404(Profile, uuid=profile_uuid, human=self.request.user)
        profile_form = ProfileEditForm(instance=profile)
        context = {'profile': profile, 'profile_form': profile_form}

        profiletype_info = self.related_models.get(profile.profiletype.lower())
        if not profiletype_info:
            return render(request, self.template_name, context)

        model_class = profiletype_info['model']
        form_class = profiletype_info['form']
        subforms = profiletype_info.get('subforms', {})
        obj = model_class.objects.filter(profile=profile).first()
        related_form = form_class(instance=obj)

        subformsets = {}
        for key, sub in subforms.items():
            formset_class = sub.get('formset')
            if formset_class:
                subformsets[key] = formset_class(
                    instance=obj,
                    queryset=getattr(obj, key).all() if obj else formset_class.model.objects.none(),
                    prefix=key
                )

        context.update({
            'related_form': related_form,
            'related_obj': obj,
            'related_type': profile.profiletype,
            'subformsets': subformsets,
        })
        return render(request, self.template_name, context)

    def post(self, request, profile_uuid):
        profile = get_object_or_404(Profile, uuid=profile_uuid, human=request.user)
        profile_form = ProfileEditForm(request.POST, request.FILES, instance=profile)

        profiletype_info = self.related_models.get(profile.profiletype.lower())
        if not profiletype_info:
            if profile_form.is_valid():
                profile_form.save()
                return redirect('profiles:detail-profile', profile_uuid=profile.uuid)
            return render(request, self.template_name, {'profile': profile, 'profile_form': profile_form})

        model_class = profiletype_info['model']
        form_class = profiletype_info['form']
        subforms = profiletype_info.get('subforms', {})

        related_obj, created = model_class.objects.get_or_create(profile=profile, defaults={'human': request.user})
        related_form = form_class(request.POST, request.FILES, instance=related_obj)

        subformsets = {}
        for key, sub in subforms.items():
            if 'formset' in sub:
                formset_class = sub['formset']
                fs = formset_class(
                    request.POST,
                    request.FILES,
                    instance=related_obj,
                    prefix=key
                )
                subformsets[key] = fs

        all_valid = (
            profile_form.is_valid()
            and related_form.is_valid()
            and all(fs.is_valid() for fs in subformsets.values()))

        if not all_valid:
            context = {
                'profile': profile,
                'profile_form': profile_form,
                'related_form': related_form,
                'related_type': profile.profiletype,
                'subformsets': subformsets
            }
            return render(request, self.template_name, context)

        # Save all forms safely
        profile_form.save()
        related_obj = related_form.save(commit=False)
        related_obj.profile = profile
        related_obj.human = request.user
        related_obj.save()

        for key, fs in subformsets.items():
            fs.instance = related_obj
            fs.save()

        if profile.profiletype.lower() == 'race':
            qr_dir = os.path.join(settings.MEDIA_ROOT, "qrcodes")
            os.makedirs(qr_dir, exist_ok=True)
            qr_filename = f"race_{profile.uuid}.png"
            full_file = os.path.join(qr_dir, qr_filename)
            if os.path.isfile(full_file) == False:
                join_url = "https://" + request.build_absolute_uri(
                    reverse('races:race_join',kwargs={'profile_uuid': profile.uuid}))
                qr = qrcode.QRCode(
                    version=1,
                    error_correction=qrcode.constants.ERROR_CORRECT_H,
                    box_size=8,
                    border=4)
                qr.add_data(join_url)
                qr.make(fit=True)
                img = qr.make_image(fill_color="black", back_color="white")
                img.save(full_file)

        return redirect('profiles:detail-profile', profile_uuid=profile.uuid)

class ProfilesListView(LoginRequiredMixin, ListView):
    model = Profile
    template_name = 'profiles/profiles.html'
    context_object_name = 'profiles'
    login_url = '/humans/login/'
    def get_queryset(self):
        return Profile.objects.filter(human=self.request.user).order_by('profiletype', 'displayname')


class ProfileBuildView(LoginRequiredMixin, CreateView):
    model = Profile
    form_class = ProfileCreateForm
    template_name = 'profiles/profile_build.html'
    login_url = '/humans/login/'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['profiletype'] = self.request.GET.get('profiletype', '').upper()
        return context

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        profiletype_param = self.request.GET.get('profiletype', '').upper()
        allowed_types = [choice[0] for choice in Profile.PROFILE_TYPE_CHOICES]
        if profiletype_param in allowed_types:
            form.fields['profiletype'].initial = profiletype_param
            form.fields['profiletype'].widget = forms.HiddenInput()
        return form

    def form_valid(self, form):
        form.instance.human = self.request.user
        self.object = form.save()
        return redirect('profiles:detail-profile', profile_uuid=self.object.uuid)


class ProfileDetailView(LoginRequiredMixin, DetailView):
    model = Profile
    template_name = 'profiles/profile_detail.html'
    context_object_name = 'profile'
    pk_url_kwarg = 'profile_uuid'

    related_models = {
        'model': Build,
        'club': Club,
        'race': Race,
        'track': Track,
        'event': Event,
        'location': Location,
        'store': Store,
        'team': Team,
    }

    def get_object(self, queryset=None):
        # Enforce ownership so user cannot open someone else's profile
        return get_object_or_404(
            Profile,
            uuid=self.kwargs['profile_uuid'],
            human=self.request.user
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        profile = self.object

        # Posts with images
        context['posts_with_images'] = (
            profile.posts.filter(image__isnull=False).exclude(image='')
        )

        # Related model data by profiletype
        related_objs = {}
        profile_type_lower = profile.profiletype.lower()

        for key, model_class in self.related_models.items():
            if key == profile_type_lower:
                try:
                    # Special case for clubs (extra relations)
                    if model_class._meta.model_name == 'club':
                        obj = model_class.objects.get(profile=profile)
                        related_objs[key] = {
                            'object': obj,
                            'locations': obj.locations.all(),
                        }
                    else:
                        obj = model_class.objects.filter(profile=profile).first()
                        related_objs[key] = {'object': obj} if obj else None

                except model_class.DoesNotExist:
                    related_objs[key] = None

        context['related_objs'] = related_objs
        return context

class ProfileDeleteView(LoginRequiredMixin, DeleteView):
    model = Profile
    template_name = 'profiles/confirm_delete.html'
    pk_url_kwarg = 'profile_uuid'
    login_url = '/humans/login/'
    def get_object(self, queryset=None):
        profile = get_object_or_404(Profile, pk=self.kwargs['profile_uuid'], human=self.request.user)
        if profile.human != self.request.user:
            return redirect('profiles:detail-profile', profile_uuid=profile.uuid)
        return profile
    def post(self, request, *args, **kwargs):
        profile = self.get_object()
        if profile.human != request.user:
            return redirect('profiles:detail-profile', profile_uuid=profile.uuid)
        # Soft-delete
        profile.deleted = True
        profile.save()
        return redirect('/profiles/')

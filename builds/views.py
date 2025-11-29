from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, View, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from .models import Build
from profiles.models import Profile
from .forms import BuildForm

class BuildListView(LoginRequiredMixin, ListView):
    model = Build
    template_name = 'builds/build_list.html'
    context_object_name = 'builds'

    def get_queryset(self):
        return Build.objects.filter(human=self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['profiles'] = Profile.objects.filter(human=self.request.user, profiletype='MODEL')
        context['unbuilt_models'] = Profile.objects.filter(human=self.request.user, profiletype='MODEL').exclude(uuid__in=Build.objects.values_list('profile__uuid', flat=True))
        return context

class BuildBuildView(LoginRequiredMixin, View):
    template_name = 'builds/build_build.html'

    def get_profile(self, profile_uuid):
        profile = get_object_or_404(Profile, uuid=profile_uuid, human=self.request.user)
        return profile

    def get(self, request, profile_uuid):
        profile = self.get_profile(profile_uuid)
        if not profile:
            return redirect('profiles:detail-profile', profile_uuid)
        if profile.human != self.request.user:
            return redirect('profiles:detail-profile', profile_uuid)

        existing_build = Build.objects.filter(profile=profile).first()
        if existing_build:
            return redirect('profiles:detail-profile', profile_uuid=profile.uuid)

        form = BuildForm()
        return render(request, self.template_name, {'form': form, 'profile': profile})

    def post(self, request, profile_uuid):
        profile = self.get_profile(profile_uuid)
        if not profile:
            return redirect('profiles:detail-profile', profile_uuid)

        existing_build = Build.objects.filter(profile=profile).first()
        if existing_build:
            return redirect('profiles:detail-profile', profile_uuid=profile.id)

        form = BuildForm(request.POST)
        if form.is_valid():
            build = form.save(commit=False)
            build.profile = profile
            build.human = request.user
            build.save()
            return redirect('profiles:detail-profile', profile.uuid)
        return render(request, self.template_name, {'form': form, 'profile': profile})

# ========================================
# 5️⃣ Delete build (safe via queryset)
# ========================================
class BuildDeleteView(LoginRequiredMixin, DeleteView):
    model = Build
    template_name = 'builds/build_confirm_delete.html'
    success_url = reverse_lazy('builds:build_list')

    def get_queryset(self):
        return Build.objects.filter(human=self.request.user)

    def get_success_url(self):
        return reverse_lazy('profiles:detail-profile',kwargs={'profile_uuid': self.object.profile.uuid})

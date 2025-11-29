# drivers/views.py
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views import View
from profiles.models import Profile
from .forms import DriverProfileForm

class DriverListView(LoginRequiredMixin, View):
    template_name = "drivers/driver_list.html"

    def get(self, request):
        drivers = Profile.objects.filter(human=request.user, profiletype='DRIVER')
        return render(request, self.template_name, {"drivers": drivers})


class DriverUpdateView(LoginRequiredMixin, View):
    template_name = "drivers/driver_update.html"

    def get(self, request, profile_uuid):
        profile = get_object_or_404(Profile, uuid=profile_uuid, human=request.user, profiletype='DRIVER')
        form = DriverProfileForm(instance=profile)
        return render(request, self.template_name, {"form": form, "profile": profile})

    def post(self, request, profile_uuid):
        profile = get_object_or_404(Profile, uuid=profile_uuid, human=request.user, profiletype='DRIVER')
        form = DriverProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            return redirect('drivers:driver_list')
        return render(request, self.template_name, {"form": form, "profile": profile})

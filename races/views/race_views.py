from django.views import View
from django.shortcuts import get_object_or_404, redirect
from django.http import HttpResponseForbidden
from django.urls import reverse
from django.conf import settings
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Count
from django.http import HttpResponseForbidden
from django.shortcuts import get_object_or_404, render, redirect
from django.urls import reverse_lazy, reverse
from django.views import View
from django.views.generic import ListView, View, DeleteView
from profiles.models import Profile
from ..models import Race, RaceDriver
from ..forms import RaceForm
import os
import qrcode

class RaceListView(LoginRequiredMixin, ListView):
    model = Profile
    template_name = "races/race_list.html"
    context_object_name = "profiles"
    def get_queryset(self):
        return (
            Profile.objects
            .filter(profiletype="RACE", human=self.request.user)
            .select_related("human")
            .annotate(driver_count=Count("race__race_drivers"))
            .order_by("displayname"))

class RaceBuildView(View):
    template_name = "races/race_build.html"

    def dispatch(self, request, *args, **kwargs):
        self.profile = get_object_or_404(Profile, uuid=kwargs["profile_uuid"], human=self.request.user)
        existing_race = Race.objects.filter(profile=self.profile).first()
        if existing_race:
            return redirect("profiles:detail-profile", profile_uuid=self.profile.uuid)
        return super().dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        form = RaceForm()
        return render(request, self.template_name, {"form": form, "profile": self.profile})

    def post(self, request, *args, **kwargs):
        form = RaceForm(request.POST)
        if form.is_valid():
            race = form.save(commit=False)
            race.profile = self.profile
            race.human = request.user
            race.save()
            join_url = "https://" + request.build_absolute_uri(
                reverse('races:race_join', kwargs={'profile_uuid': self.profile.uuid}))
            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_H,
                box_size=8,
                border=4)
            qr.add_data(join_url)
            qr.make(fit=True)
            img = qr.make_image(fill_color="black", back_color="white")
            qr_dir = os.path.join(settings.MEDIA_ROOT, "qrcodes")
            os.makedirs(qr_dir, exist_ok=True)
            qr_filename = f"race_{self.profile.uuid}.png"
            img.save(os.path.join(qr_dir, qr_filename))
            return redirect("profiles:detail-profile", profile_uuid=self.profile.uuid)
        return render(self.template_name, {"form": form, "profile": self.profile})

class RaceDeleteView(LoginRequiredMixin, DeleteView):
    model = Race
    template_name = "races/race_confirm_delete.html"
    def get_object(self):
        profile = get_object_or_404(Profile, uuid=self.kwargs["profile_uuid"], human=self.request.user)
        return getattr(profile, "race", None)
    def get_success_url(self):
        return reverse_lazy("races:race_list")

class RaceJoinView(LoginRequiredMixin, View):
    template_name = "races/race_join.html"
    def get(self, request, profile_uuid):
        profile = get_object_or_404(Profile, uuid=profile_uuid)
        race = get_object_or_404(Race, profile_id=profile.id)
        if race.entry_locked==True:
            return render(request, "races/race_full.html", {'profile': profile})
        driver_profiles = Profile.objects.filter(human=request.user, profiletype="DRIVER")
        model_profiles = Profile.objects.filter(human=request.user, profiletype="MODEL")
        context = {
            "race": race,
            "driver_profiles": driver_profiles,
            "model_profiles": model_profiles,
        }
        return render(request, self.template_name, context)
    def post(self, request, profile_uuid):
        profile = get_object_or_404(Profile, uuid=profile_uuid)
        race = get_object_or_404(Race, profile_id=profile.id)
        if race.entry_locked==True:
            return redirect("profiles:detail-profile", profile_uuid=race.profile.uuid)
        driver_id = request.POST.get("driver_id")
        model_id = request.POST.get("model_id")
        transponder = request.POST.get("transponder")
        driver_profile = Profile.objects.filter(id=driver_id, human=request.user, profiletype="DRIVER").first() if driver_id else None
        model_profile = Profile.objects.filter(id=model_id, human=request.user, profiletype="MODEL").first() if model_id else None
        existing = RaceDriver.objects.filter(
            race=race,
            human=request.user,
            driver=driver_profile,
            model=model_profile
        ).exists()
        if not existing:
            RaceDriver.objects.create(
                race=race,
                human=request.user,
                driver=driver_profile,
                model=model_profile,
                transponder=transponder,
            )
        return redirect("profiles:detail-profile", profile_uuid=race.profile.uuid)

class RaceLockToggleView(View):
    def post(self, request, profile_uuid, race_uuid):
        race = get_object_or_404(Race, uuid=race_uuid, human=self.request.user)
        if race.race_finished==True:
            return HttpResponseForbidden("Race is already finished.")
        if race.entry_locked==True:
            race.entry_locked=False
        else:
            race.entry_locked=True
        race.save()
        return redirect(reverse("races:race_crawler_comp", kwargs={"profile_uuid": profile_uuid, "race_uuid":race_uuid}))

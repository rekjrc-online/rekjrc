from django.conf import settings
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Count, Max
from django.shortcuts import get_object_or_404, render, redirect
from django.urls import reverse_lazy, reverse
from django.views import View
from django.views.generic import ListView, View, DeleteView
from profiles.models import Profile
from .models import Race, RaceDriver, LapMonitorResult, RaceDragRace, RaceCrawlerRun, CrawlerRunLog
from .forms import RaceForm
from io import TextIOWrapper
import random
import math
import json
import csv
import os
import qrcode

class RaceCrawlerCompView(View):
    template_name = 'races/race_crawler_comp.html'

    def get(self, request, profile_id, race_id):
        race = get_object_or_404(Race, id=race_id)
        racedrivers = RaceDriver.objects.filter(race=race).order_by('id')
        for driver in racedrivers:
            driver.run = RaceCrawlerRun.objects.filter(race=race, racedriver=driver).first()
        return render(request, self.template_name, {
            'race': race,
            'racedrivers': racedrivers,
        })

class RaceCrawlerRunView(View):
    template_name = 'races/race_crawler_run.html'

    def get(self, request, profile_id, race_id, racedriver_id):
        race = get_object_or_404(Race, id=race_id)
        racedriver = get_object_or_404(RaceDriver, id=racedriver_id)
        run, _ = RaceCrawlerRun.objects.get_or_create(race=race, racedriver=racedriver)
        return render(request, self.template_name, {
            'race': race,
            'racedriver': racedriver,
            'run': run
        })

    def post(self, request, profile_id, race_id, racedriver_id):
        run = get_object_or_404(RaceCrawlerRun, race_id=race_id, racedriver_id=racedriver_id)

        # Update elapsed time and penalty points
        elapsed = request.POST.get('elapsed_time')
        points = request.POST.get('penalty_points')
        if elapsed is not None:
            run.elapsed_time = float(elapsed)
        if points is not None:
            run.penalty_points = int(points)
        run.save()

        # Handle CrawlerRunLog JSON
        run_log_json = request.POST.get('run_log')
        if run_log_json:
            try:
                log_entries = json.loads(run_log_json)
                # Optional: clear existing log entries
                run.log_entries.all().delete()

                for entry in log_entries:
                    CrawlerRunLog.objects.create(
                        run=run,
                        human=run.racedriver.human,
                        driver=run.racedriver.driver,
                        model=run.racedriver.model,
                        milliseconds=entry['milliseconds'],
                        label=entry['label'],
                        delta=entry['delta'],
                    )
            except (json.JSONDecodeError, KeyError, TypeError) as e:
                # Optionally log the error
                print(f"Failed to save run log: {e}")

        return redirect(
            'races:race_crawler_comp',
            profile_id=profile_id,
            race_id=race_id,
        )


class RaceDragRaceView(LoginRequiredMixin, View):
    template_name = "races/race_drag_race.html"

    def get(self, request, profile_id, race_id):
        race = get_object_or_404(Race, pk=race_id)
        if race.human != request.user:
            return redirect("profiles:detail-profile", profile_id=race.profile.id)

        drag_rounds = RaceDragRace.objects.filter(race=race).order_by("round_number", "id")

        if not drag_rounds.exists():
            # --- ROUND 1: initialize bracket ---
            drivers = list(RaceDriver.objects.filter(race=race))
            random.shuffle(drivers)
            num_entrants = len(drivers)

            if num_entrants < 2:
                return render(request, self.template_name, {
                    "race": race,
                    "rounds": [],
                    "message": "Not enough drivers to start drag race."
                })

            next_power_of_2 = 2 ** math.ceil(math.log2(num_entrants))
            total_matches = next_power_of_2 // 2
            num_byes = next_power_of_2 - num_entrants

            i = 0
            for match in range(total_matches):
                if match < num_byes:
                    model1 = drivers[i]
                    model2 = None
                    i += 1
                else:
                    model1 = drivers[i]
                    model2 = drivers[i + 1] if i + 1 < num_entrants else None
                    i += 2

                RaceDragRace.objects.create(
                    race=race,
                    model1=model1,
                    model2=model2,
                    winner=None,
                    round_number=1
                )

            drag_rounds = RaceDragRace.objects.filter(race=race).order_by("round_number", "id")

        # --- LATER ROUNDS ---
        else:
            max_round = drag_rounds.aggregate(max_round_number=Max("round_number"))["max_round_number"]
            last_round_records = drag_rounds.filter(round_number=max_round)

            # Only proceed when all winners for the last round are known
            if all(r.winner for r in last_round_records):
                winners = [r.winner for r in last_round_records]

                # 🧩 keep order: 1v2, 3v4, etc.  (no shuffle!)
                if len(winners) == 1:
                    # Tournament complete
                    return render(request, self.template_name, {
                        "race": race,
                        "rounds": drag_rounds,
                        "final_winner": winners[0],
                    })

                for i in range(0, len(winners), 2):
                    model1 = winners[i]
                    model2 = winners[i + 1] if i + 1 < len(winners) else None

                    RaceDragRace.objects.create(
                        race=race,
                        model1=model1,
                        model2=model2,
                        winner=None,
                        round_number=max_round + 1
                    )

                drag_rounds = RaceDragRace.objects.filter(race=race).order_by("round_number", "id")

        return render(request, self.template_name, {"race": race, "rounds": drag_rounds})

    def post(self, request, profile_id, race_id):
        race = get_object_or_404(Race, id=race_id)
        if race.human != request.user:
            return redirect("profiles:detail-profile", profile_id=race.profile.id)
        if race.human != request.user:
            return redirect("profiles:detail-profile", profile_id=race.profile.id)
        for drag_round in RaceDragRace.objects.filter(race=race):
            winner_id = request.POST.get(f"winner_{drag_round.id}")
            if winner_id:
                winner_driver = RaceDriver.objects.filter(id=winner_id).first()
                if winner_driver:
                    drag_round.winner = winner_driver
                    drag_round.save()
        return redirect("races:race_drag_race", profile_id=profile_id, race_id=race_id)

class LapMonitorUploadView(LoginRequiredMixin, View):
    template_name = "races/lapmonitor_upload.html"

    def get(self, request, race_id):
        race = get_object_or_404(Race, pk=race_id)
        if race.human != request.user:
            return redirect("profiles:detail-profile", profile_id=race.profile.id)
        return render(request, self.template_name, {"race": race})

    def post(self, request, race_id):
        race = get_object_or_404(Race, pk=race_id)
        if race.human != request.user:
            return redirect("profiles:detail-profile", profile_id=race.profile.id)

        file = request.FILES.get("file")
        if not file:
            messages.error(request, "❌ No file selected.")
            return redirect("races:upload_lapmonitor", race_id=race.id)

        try:
            data = TextIOWrapper(file.file, encoding="utf-8")
            reader = csv.DictReader(data)
            reader.fieldnames = [n.strip().lower().replace(" ", "_") for n in reader.fieldnames]
            created_count = 0
            skipped_count = 0

            for row in reader:
                try:
                    if not row.get("driver_id") or not row.get("lap_index"):
                        skipped_count += 1
                        continue
                    if LapMonitorResult.objects.filter(
                        race=race,
                        driver_id=row.get("driver_id"),
                        lap_index=row.get("lap_index")
                    ).exists():
                        skipped_count += 1
                        continue
                    LapMonitorResult.objects.create(
                        race=race,
                        session_id=row.get("session_id"),
                        session_name=row.get("session_name"),
                        session_date=row.get("session_date"),
                        session_kind=row.get("session_kind"),
                        session_duration=float(row.get("session_duration") or 0),
                        driver_id=row.get("driver_id"),
                        driver_name=row.get("driver_name"),
                        driver_transponder_id=row.get("driver_transponder_id"),
                        driver_rank=int(row.get("driver_rank") or 0),
                        lap_index=int(row.get("lap_index") or 0),
                        lap_end_time=float(row.get("lap_end_time") or 0),
                        lap_duration=float(row.get("lap_duration") or 0),
                        lap_kind=row.get("lap_kind"),
                    )
                    created_count += 1
                except Exception:
                    skipped_count += 1

            messages.success(request, f"✅ Imported {created_count} new results, skipped {skipped_count} rows.")

        except Exception as e:
            messages.error(request, f"❌ Error processing CSV: {e}")

        return redirect("profiles:detail-profile", profile_id=race.profile.id)


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
        self.profile = get_object_or_404(Profile, id=kwargs["profile_id"], human=self.request.user)
        existing_race = Race.objects.filter(profile=self.profile).first()
        if existing_race:
            return redirect("profiles:detail-profile", profile_id=self.profile.id)
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
                reverse('races:race_join', kwargs={'profile_id': self.profile.id}))
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
            qr_filename = f"race_{self.profile.id}.png"
            img.save(os.path.join(qr_dir, qr_filename))
            return redirect("profiles:detail-profile", profile_id=self.profile.id)
        return render(self.template_name, {"form": form, "profile": self.profile})

class RaceDeleteView(LoginRequiredMixin, DeleteView):
    model = Race
    template_name = "races/race_confirm_delete.html"
    def get_object(self):
        profile = get_object_or_404(Profile, id=self.kwargs["profile_id"], human=self.request.user)
        return getattr(profile, "race", None)
    def get_success_url(self):
        return reverse_lazy("races:race_list")

class RaceJoinView(LoginRequiredMixin, View):
    template_name = "races/race_join.html"
    def get(self, request, profile_id):
        race = get_object_or_404(Race, profile_id=profile_id)
        driver_profiles = Profile.objects.filter(human=request.user, profiletype="DRIVER")
        model_profiles = Profile.objects.filter(human=request.user, profiletype="MODEL")
        context = {
            "race": race,
            "driver_profiles": driver_profiles,
            "model_profiles": model_profiles,
        }
        return render(request, self.template_name, context)
    def post(self, request, profile_id):
        race = get_object_or_404(Race, profile_id=profile_id)
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
        return redirect("profiles:detail-profile", profile_id=race.profile.id)

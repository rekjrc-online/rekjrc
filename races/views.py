from django.conf import settings
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Count, Max
from django.shortcuts import get_object_or_404, render, redirect
from django.urls import reverse_lazy, reverse
from django.views import View
from django.views.generic import ListView, View, DeleteView
from profiles.models import Profile
from posts.models import Post
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

    def get(self, request, profile_uuid, race_uuid):
        race = get_object_or_404(Race, uuid=race_uuid)
        racedrivers = RaceDriver.objects.filter(race=race).order_by('id')
        for driver in racedrivers:
            driver.run = RaceCrawlerRun.objects.filter(race=race, racedriver=driver).first()
        return render(request, self.template_name, {
            'race': race,
            'racedrivers': racedrivers,
        })

class RaceCrawlerRunView(View):
    template_name = 'races/race_crawler_run.html'

    def get(self, request, profile_uuid, race_uuid, racedriver_uuid):
        race = get_object_or_404(Race, uuid=race_uuid)
        racedriver = get_object_or_404(RaceDriver, uuid=racedriver_uuid)
        run, _ = RaceCrawlerRun.objects.get_or_create(race=race, racedriver=racedriver)
        return render(request, self.template_name, {
            'race': race,
            'racedriver': racedriver,
            'run': run
        })

    def post(self, request, profile_uuid, race_uuid, racedriver_uuid):
        racedriver = get_object_or_404(RaceDriver, uuid=racedriver_uuid)
        print("===")
        print("RACEDRIVER",racedriver)
        print("===")
        run = get_object_or_404(RaceCrawlerRun, race_id=racedriver.race_id, racedriver_id=racedriver.id)
        print("===")
        print("RUN",run)
        print("===")

        # Update elapsed time and penalty points
        elapsed = request.POST.get('elapsed_time')
        points = request.POST.get('penalty_points')
        if elapsed is not None:
            run.elapsed_time = float(elapsed)
        if points is not None:
            run.penalty_points = int(points)
        run.save()
        print(run)

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
                post_text=str(racedriver) + '\r\n'
                post_text += 'Points: ' + str(points) + '\r\n'
                for entry in log_entries:
                    post_text += entry['label'] + '\r\n'
                    CrawlerRunLog.objects.create(
                        run=run,
                        human=run.racedriver.human,
                        driver=run.racedriver.driver,
                        model=run.racedriver.model,
                        milliseconds=entry['milliseconds'],
                        label=entry['label'],
                        delta=entry['delta'],
                    )
                if post_text:
                    race = get_object_or_404(Race, uuid=race_uuid)
                    Post.objects.create(
                        human=request.user,
                        profile=race.profile,
                        content=post_text,
                        display_content=post_text  # optional—depends how you use it
                    )
            except (json.JSONDecodeError, KeyError, TypeError) as e:
                # Optionally log the error
                print(f"Failed to save run log: {e}")

        return redirect(
            'races:race_crawler_comp',
            profile_uuid=profile_uuid,
            race_uuid=race_uuid,
        )


class RaceDragRaceView(LoginRequiredMixin, View):
    template_name = "races/race_drag_race.html"

    def get(self, request, profile_uuid, race_uuid):
        race = get_object_or_404(Race, uuid=race_uuid)
        if race.race_finished==True:
            return redirect("profiles:detail-profile", profile_uuid=profile_uuid)

        if race.human != request.user:
            return redirect("profiles:detail-profile", profile_uuid=profile_uuid)

        drag_rounds = RaceDragRace.objects.filter(race=race).order_by("round_number", "id")

        # ---------------------------------------------------
        # ROUND 1 — initialize bracket if none exists
        # ---------------------------------------------------
        if not drag_rounds.exists():
            race.entry_locked=True
            race.save()
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

        # ---------------------------------------------------
        # LATER ROUNDS — build next round when previous complete
        # ---------------------------------------------------
        else:
            max_round = drag_rounds.aggregate(max_round_number=Max("round_number"))["max_round_number"]
            last_round_records = drag_rounds.filter(round_number=max_round)

            # Proceed only when all winners for last round are chosen
            if all(r.winner for r in last_round_records):
                winners = [r.winner for r in last_round_records]

                # Tournament finished
                if len(winners) == 1:
                    return render(request, self.template_name, {
                        "race": race,
                        "rounds": drag_rounds,
                        "final_winner": winners[0],
                        "show_complete_button": True,
                    })

                # Create next round
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

    # =====================================================================
    # POST — record match winners OR complete the race
    # =====================================================================
    def post(self, request, profile_uuid, race_uuid):
        race = get_object_or_404(Race, uuid=race_uuid)
        if race.race_finished==True:
            return redirect("profiles:detail-profile", profile_uuid=profile_uuid)
        if race.human != request.user:
            return redirect("profiles:detail-profile", profile_uuid=profile_uuid)

        # ---------------------------------------------------
        # COMPLETE RACE BUTTON
        # ---------------------------------------------------
        if "complete_race" in request.POST:
            final_winner_id = request.POST.get("final_winner")
            final_winner = RaceDriver.objects.filter(id=final_winner_id).first()

            if final_winner:
                profile = race.profile
                human = race.human
                content = f"🏁 Winner 🏁\r\nDriver: {final_winner.driver.displayname}\r\nModel: {final_winner.model.displayname}" + "\r\n"
                drag_rounds = RaceDragRace.objects.filter(race=race).order_by("round_number", "id")
                last_round=0
                for round in drag_rounds:
                    if round.round_number!=last_round:
                        content += "\r\n=Round " + str(round.round_number) + "=\r\n"
                        last_round=round.round_number
                    if(round.winner==round.model1):
                        content+="🏁" + str(round.model1.driver.displayname) + " vs " + str(round.model2.driver.displayname) + "\r\n"
                    else:
                        content+=str(round.model1.driver.displayname) + " vs " + "🏁" + str(round.model2.driver.displayname) + "\r\n"

                Post.objects.create(
                    human=human,
                    profile=profile,
                    content=content,
                    display_content=content,
                )

                race.race_finished=True
                race.save()

            return redirect("/")

        # ---------------------------------------------------
        # NORMAL WINNER SUBMISSION
        # ---------------------------------------------------
        for drag_round in RaceDragRace.objects.filter(race=race):
            winner_id = request.POST.get(f"winner_{drag_round.id}")
            if winner_id:
                winner_driver = RaceDriver.objects.filter(id=winner_id).first()
                if winner_driver:
                    drag_round.winner = winner_driver
                    drag_round.save()

        return redirect("races:race_drag_race", profile_uuid=profile_uuid, race_uuid=race_uuid)


class LapMonitorUploadView(LoginRequiredMixin, View):
    template_name = "races/lapmonitor_upload.html"

    def get(self, request, race_uuid):
        race = get_object_or_404(Race, uuid=race.uuid)
        if race.human != request.user:
            return redirect("profiles:detail-profile", profile_uuid=race.profile.uuid)
        return render(request, self.template_name, {"race": race})

    def post(self, request, race_uuid):
        race = get_object_or_404(Race, uuid=race.uuid)
        if race.human != request.user:
            return redirect("profiles:detail-profile", profile_uuid=race.profile.uuid)

        file = request.FILES.get("file")
        if not file:
            messages.error(request, "❌ No file selected.")
            return redirect("races:upload_lapmonitor", race_uuid=race.uuid)

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

        return redirect("profiles:detail-profile", profile_uuid=race.profile.uuid)


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

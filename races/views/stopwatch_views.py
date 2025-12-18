from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponseForbidden
from django.shortcuts import get_object_or_404, render, redirect
from django.urls import reverse
from django.views import View
from django.views.generic import View
from profiles.models import Profile
from posts.models import Post
from ..models import Race, RaceDriver, RaceStopwatchRun

class StopwatchRaceListView(View):
    template_name = 'races/stopwatch_race_list.html'
    def get(self, request, profile_uuid, race_uuid):
        race = get_object_or_404(Race, uuid=race_uuid)
        racedrivers = RaceDriver.objects.filter(race=race).order_by('id')
        for driver in racedrivers:
            driver.run = RaceStopwatchRun.objects.filter(race=race, racedriver=driver).first()
        return render(request, self.template_name, {
            'race': race,
            'racedrivers': racedrivers,
        })

class StopwatchRaceRunView(View):
    template_name = 'races/stopwatch_race_run.html'
    def get(self, request, profile_uuid, race_uuid, racedriver_uuid):
        race = get_object_or_404(Race, uuid=race_uuid)
        if race.race_finished==True:
            return HttpResponseForbidden("Race is already finished.")
        racedriver = get_object_or_404(RaceDriver, uuid=racedriver_uuid)
        run, _ = RaceStopwatchRun.objects.get_or_create(race=race, racedriver=racedriver)
        return render(request, self.template_name, {
            'race': race,
            'racedriver': racedriver,
            'run': run
        })

    def post(self, request, profile_uuid, race_uuid, racedriver_uuid):
        race = get_object_or_404(Race, uuid=race_uuid)
        racedriver = get_object_or_404(RaceDriver, uuid=racedriver_uuid)
        run = get_object_or_404(RaceStopwatchRun, race_id=racedriver.race_id, racedriver_id=racedriver.id)
        elapsed = request.POST.get('elapsed_time')
        if elapsed is not None:
            run.elapsed_time = float(elapsed)
        run.save()
        post_text=str(racedriver) + '\r\n'
        post_text += 'Elapsed Time: ' + str(elapsed) + '\r\n'
        Post.objects.create(
            human=request.user,
            profile=race.profile,
            content=post_text
        )
        return redirect(
            'races:stopwatch_race_list',
            profile_uuid=profile_uuid,
            race_uuid=race_uuid,
        )

class StopwatchRaceFinishView(LoginRequiredMixin, View):
    def post(self, request, profile_uuid, race_uuid, *args, **kwargs):
        profile = get_object_or_404(Profile, uuid=profile_uuid)
        if profile.human != request.user:
            return HttpResponseForbidden("You are not allowed to finish this race.")
        race = get_object_or_404(Race, profile=profile.id, uuid=race_uuid)
        if not race:
            return HttpResponseForbidden("Race does not exist.")
        if race.race_finished==True:
            return HttpResponseForbidden("Race is already finished.")
        runs = RaceStopwatchRun.objects.filter(
            race=race
        ).select_related('racedriver', 'racedriver__driver', 'racedriver__model')
        if not runs.exists():
            return HttpResponseForbidden("No runs found.")
        sorted_runs = runs.order_by('elapsed_time')
        winner = sorted_runs[0]
        content = f"🏁 Winner 🏁\r\nDriver: {winner.racedriver.driver.displayname}\r\nModel: {winner.racedriver.model.displayname}\r\nElapsed Time: {winner.elapsed_time}\r\n"
        result_lines = [content]
        for idx, run in enumerate(sorted_runs, start=1):
            driver_name = run.racedriver.driver.displayname if run.racedriver.driver else '-driver-'
            model_name = run.racedriver.model.displayname if run.racedriver.model else '-model-'
            elapsed = f"{run.elapsed_time:.2f}s" if run.elapsed_time is not None else "No time"
            result_lines.append(f"{idx}. {driver_name} | {model_name} | {elapsed}")
        results_text = "\r\n".join(result_lines) or "No runs recorded."
        Post.objects.create(
            human=request.user,
            profile=profile,
            content=results_text
        )
        race.race_finished = True
        race.entry_locked = True
        race.save()
        return redirect(reverse("profiles:detail-profile", kwargs={"profile_uuid": profile.uuid}))

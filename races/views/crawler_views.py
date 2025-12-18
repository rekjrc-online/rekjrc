from django.views import View
from ..models import Race, RaceDriver, RaceCrawlerRun, CrawlerRunLog
from django.shortcuts import get_object_or_404, redirect, render
from django.http import HttpResponseForbidden
from django.urls import reverse
from django.contrib.auth.mixins import LoginRequiredMixin
from posts.models import Post
from profiles.models import Profile
import json

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

class RaceCrawlerFinishView(LoginRequiredMixin, View):
    def post(self, request, profile_uuid, race_uuid, *args, **kwargs):
        profile = get_object_or_404(Profile, uuid=profile_uuid)
        if profile.human != request.user:
            return HttpResponseForbidden("You are not allowed to finish this race.")
        race = get_object_or_404(Race, profile=profile.id, uuid=race_uuid)
        if not race:
            return HttpResponseForbidden("Race does not exist.")
        if race.race_finished==True:
            return HttpResponseForbidden("Race is already finished.")
        runs = RaceCrawlerRun.objects.filter(
            race=race
        ).select_related('racedriver', 'racedriver__driver', 'racedriver__model')
        if not runs.exists():
            return HttpResponseForbidden("No runs found.")
        race.race_finished = True
        race.entry_locked = True
        race.save()
        sorted_runs = runs.order_by('penalty_points', 'elapsed_time')  # elapsed_time secondary
        lowest_points = sorted_runs.first().penalty_points
        winners = [run for run in sorted_runs if run.penalty_points == lowest_points]
        if len(winners) == 1:
            winner = winners[0]
            content = f"🏁 Winner 🏁\r\nDriver: {winner.racedriver.driver.displayname}\r\nModel: {winner.racedriver.model.displayname}\r\n"
        else:
            content = "🏁 Winners (tie) 🏁\r\n"
            for run in winners:
                content += f"Driver: {run.racedriver.driver.displayname} | Model: {run.racedriver.model.displayname}\r\n"
        result_lines = [content]
        for idx, run in enumerate(sorted_runs, start=1):
            driver_name = run.racedriver.driver.displayname if run.racedriver.driver else '-driver-'
            model_name = run.racedriver.model.displayname if run.racedriver.model else '-model-'
            elapsed = f"{run.elapsed_time:.2f}s" if run.elapsed_time is not None else "No time"
            points = run.penalty_points
            result_lines.append(f"{idx}. {driver_name} | {model_name} | {points} pts | {elapsed}")
        results_text = "\r\n".join(result_lines) or "No runs recorded."
        Post.objects.create(
            human=request.user,
            profile=profile,
            content=results_text
        )
        return redirect(reverse("profiles:detail-profile", kwargs={"profile_uuid": profile.uuid}))

class RaceCrawlerRunView(View):
    template_name = 'races/race_crawler_run.html'
    def get(self, request, profile_uuid, race_uuid, racedriver_uuid):
        race = get_object_or_404(Race, uuid=race_uuid)
        if race.race_finished==True:
            return HttpResponseForbidden("Race is already finished.")
        racedriver = get_object_or_404(RaceDriver, uuid=racedriver_uuid)
        run, _ = RaceCrawlerRun.objects.get_or_create(race=race, racedriver=racedriver)
        return render(request, self.template_name, {
            'race': race,
            'racedriver': racedriver,
            'run': run
        })

    def post(self, request, profile_uuid, race_uuid, racedriver_uuid):
        racedriver = get_object_or_404(RaceDriver, uuid=racedriver_uuid)
        run = get_object_or_404(RaceCrawlerRun, race_id=racedriver.race_id, racedriver_id=racedriver.id)
        elapsed = request.POST.get('elapsed_time')
        points = request.POST.get('penalty_points')
        if elapsed is not None:
            run.elapsed_time = float(elapsed)
        if points is not None:
            run.penalty_points = int(points)
        run.save()
        print(run)
        run_log_json = request.POST.get('run_log')
        if run_log_json:
            try:
                log_entries = json.loads(run_log_json)
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
                        content=post_text
                    )
            except (json.JSONDecodeError, KeyError, TypeError) as e:
                print(f"Failed to save run log: {e}")
        return redirect(
            'races:race_crawler_comp',
            profile_uuid=profile_uuid,
            race_uuid=race_uuid,
        )

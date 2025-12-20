from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponseForbidden
from django.shortcuts import get_object_or_404, render, redirect
from django.views import View
from django.views.generic import View
from django.db.models import F
from django.db.models import Q
from profiles.models import Profile
from posts.models import Post
from ..models import Race, RaceDriver, LongJumpRun

class LongJumpListView(View):
    template_name = 'races/longjump_race_list.html'
    def get(self, request, profile_uuid, race_uuid):
        race = get_object_or_404(Race, uuid=race_uuid)
        racedrivers = RaceDriver.objects.filter(race=race).order_by('id')
        for driver in racedrivers:
            driver.run = LongJumpRun.objects.filter(race=race, racedriver=driver).first()
        return render(request, self.template_name, {
            'race': race,
            'racedrivers': racedrivers,
        })

class LongJumpRunView(View):
    template_name = 'races/longjump_race_run.html'
    def get(self, request, profile_uuid, race_uuid, racedriver_uuid):
        race = get_object_or_404(Race, uuid=race_uuid)
        if race.race_finished==True:
            return HttpResponseForbidden("Race is already finished.")
        racedriver = get_object_or_404(RaceDriver, uuid=racedriver_uuid)
        run, _ = LongJumpRun.objects.get_or_create(race=race, racedriver=racedriver)
        return render(request, self.template_name, {
            'race': race,
            'racedriver': racedriver,
            'run': run
        })

    def post(self, request, profile_uuid, race_uuid, racedriver_uuid):
        race = get_object_or_404(Race, uuid=race_uuid)
        racedriver = get_object_or_404(RaceDriver, uuid=racedriver_uuid)
        run = get_object_or_404(LongJumpRun, race_id=racedriver.race_id, racedriver_id=racedriver.id)
        feet = request.POST.get('feet')
        inches = request.POST.get('inches')
        if feet is not None: run.feet = int(feet)
        if inches is not None: run.inches = int(inches)
        run.save()
        post_text=str(racedriver) + '\r\n'
        post_text += 'Distance: ' + str(feet) + 'ft' + str(inches) + 'in\r\n'
        Post.objects.create(
            human=request.user,
            profile=race.profile,
            content=post_text)
        return redirect(
            'races:longjump_race_list',
            profile_uuid=profile_uuid,
            race_uuid=race_uuid)

class LongJumpFinishView(LoginRequiredMixin, View):
    def post(self, request, profile_uuid, race_uuid, *args, **kwargs):
        profile = get_object_or_404(Profile, uuid=profile_uuid)
        if profile.human != request.user:
            return HttpResponseForbidden("You are not allowed to finish this race.")
        race = get_object_or_404(Race, profile=profile.id, uuid=race_uuid)
        if not race:
            return HttpResponseForbidden("Race does not exist.")
        if race.race_finished==True:
            return HttpResponseForbidden("Race is already finished.")
        runs = (LongJumpRun.objects
            .filter(race=race)
            .filter(Q(feet__gt=0) | Q(inches__gt=0))
            .select_related('racedriver', 'racedriver__driver', 'racedriver__model')
        )
        print(runs[0])
        if not runs.exists():
            return HttpResponseForbidden("No runs found.")
        sorted_runs = runs.order_by('-feet','-inches')
        winner = sorted_runs[0]
        content = f"🏁 Winner 🏁\r\nDriver: {winner.racedriver.driver.displayname}\r\nModel: {winner.racedriver.model.displayname}\r\nDistance: {winner.feet}'{winner.inches}\"\r\n"
        result_lines = [content]
        for idx, run in enumerate(sorted_runs, start=1):
            if run.feet > 0 or run.inches > 0:
                distance = run
            else:
                distance = "No time"
            result_lines.append(f"{idx}. {distance}")
        results_text = "\r\n".join(result_lines) or "No runs recorded."
        Post.objects.create(
            human=request.user,
            profile=profile,
            content=results_text
        )
        race.race_finished = True
        race.entry_locked = True
        race.save()
        return redirect(
            'races:longjump_race_list',
            profile_uuid=profile_uuid,
            race_uuid=race_uuid,
        )

from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Avg, Exists, OuterRef, Count, Subquery
from django.http import HttpResponseForbidden
from django.shortcuts import get_object_or_404, render, redirect
from django.views import View
from django.views.generic import View
from posts.models import Post
from profiles.models import Profile
from ..models import Race, RaceDriver, JudgedEventJudge, JudgedEventRun, JudgedEventRunScore


class JudgedRaceListView(View):
    template_name = 'races/judged_race_list.html'

    def get(self, request, profile_uuid, race_uuid):
        race = get_object_or_404(Race, uuid=race_uuid)
        if race.race_finished:
            return HttpResponseForbidden("Race is already finished.")
        is_race_owner = race.human == request.user
        is_judge = JudgedEventJudge.objects.filter(race=race, human=request.user).exists()
        if not (is_race_owner or is_judge):
            return HttpResponseForbidden("You are not authorized to view this race.")

        judges = (
            JudgedEventJudge.objects
            .filter(race=race)
            .select_related('human'))
        race.judge_count=len(judges)
        
        my_score_subquery = (
            JudgedEventRunScore.objects
            .filter(
                run=OuterRef('judgedeventrun'),
                judge=request.user
            )
            .values('score')[:1]
        )

        has_scored_subquery = JudgedEventRunScore.objects.filter(
            run=OuterRef('judgedeventrun'),
            judge=request.user
        )

        racedrivers = (
            RaceDriver.objects
            .filter(race=race)
            .select_related('driver', 'model')
            .annotate(
                score_count=Count('judgedeventrun__scores', distinct=True),
                score_avg=Avg('judgedeventrun__scores__score'),
                my_score=Subquery(my_score_subquery),
                has_scored=Exists(has_scored_subquery),
            )
            .order_by('id')
        )

        return render(request, self.template_name, {
            'race': race,
            'racedrivers': racedrivers,
            'judges': judges,
            'is_judge': is_judge})

class JudgedRaceRunView(View):
    template_name = 'races/judged_race_run.html'
    def get(self, request, profile_uuid, race_uuid, racedriver_uuid):
        race = get_object_or_404(Race, uuid=race_uuid)
        if race.race_finished==True:
            return HttpResponseForbidden("Race is already finished.")
        racedriver = get_object_or_404(RaceDriver, uuid=racedriver_uuid)
        return render(
            request,
            self.template_name,
            {'race': race, 'racedriver': racedriver}
        )

    def post(self, request, profile_uuid, race_uuid, racedriver_uuid):
        race = get_object_or_404(Race, uuid=race_uuid)
        if race.race_finished==True:
            return HttpResponseForbidden("Race is already finished.")
        racedriver = get_object_or_404(RaceDriver, uuid=racedriver_uuid)
        run, created = JudgedEventRun.objects.get_or_create(race=race, racedriver=racedriver)
        my_score = JudgedEventRunScore.objects.filter(run=run, judge=request.user).first()
        if my_score:
            return redirect(
                'races:judged_event_list',
                profile_uuid=profile_uuid,
                race_uuid=race_uuid,
            )
        score = request.POST.get('score')
        if score is None:
            return HttpResponseForbidden("Score cannot be empty.")
        JudgedEventRunScore.objects.create(
            run=run,
            judge=request.user,
            score=score,
        )
        return redirect(
            'races:judged_event_list',
            profile_uuid=profile_uuid,
            race_uuid=race_uuid,
        )

class JudgedRaceFinishView(LoginRequiredMixin, View):
    def post(self, request, profile_uuid, race_uuid, *args, **kwargs):
        profile = get_object_or_404(Profile, uuid=profile_uuid)
        if profile.human != request.user:
            return HttpResponseForbidden("You are not allowed to finish this race.")
        race = get_object_or_404(Race, profile=profile, uuid=race_uuid)
        if race.race_finished:
            return HttpResponseForbidden("Race is already finished.")
        runs = (
            JudgedEventRun.objects
            .filter(race=race)
            .select_related(
                'racedriver',
                'racedriver__driver',
                'racedriver__model'
            )
            .annotate(
                avg_score=Avg('scores__score'),
                score_count=Count('scores')
            )
            .filter(score_count__gt=0)  # must have at least one score
            .order_by('-avg_score')
        )
        if not runs.exists():
            return HttpResponseForbidden("No scored runs found.")

        winner = runs.first()

        # 🏁 Build results text
        lines = [
            "🏁 Winner 🏁",
            f"Driver: {winner.racedriver.driver.displayname}",
            f"Model: {winner.racedriver.model.displayname}",
            f"Average Score: {winner.avg_score:.2f}",
            "",
            "Results:"
        ]

        for idx, run in enumerate(runs, start=1):
            driver_name = run.racedriver.driver.displayname
            model_name = run.racedriver.model.displayname
            avg = f"{run.avg_score:.2f}" if run.avg_score is not None else "--"
            count = run.score_count

            lines.append(
                f"{idx}. {driver_name} | {model_name} | {avg} avg ({count} score{'s' if count != 1 else ''})"
            )

        Post.objects.create(
            human=request.user,
            profile=profile,
            content="\r\n".join(lines)
        )

        # Lock the race
        race.race_finished = True
        race.entry_locked = True
        race.save(update_fields=['race_finished', 'entry_locked'])

        return redirect(
            'races:judged_event_list',
            profile_uuid=profile_uuid,
            race_uuid=race_uuid,
        )

class JudgeJoinRaceView(View):
    template_name = 'races/judged_race_judge.html'
    def get(self, request, profile_uuid, race_uuid):
        race = get_object_or_404(Race, uuid=race_uuid)
        if race.race_finished==True:
            return HttpResponseForbidden("Race is already finished.")
        profile = get_object_or_404(Profile, uuid=profile_uuid)
        ijudges = JudgedEventJudge.objects.filter(race=race, human=request.user).first()
        print(ijudges)
        judges = JudgedEventJudge.objects.filter(race=race)
        if len(judges) >= 3:
            return HttpResponseForbidden("Race already has 3 judges.")
        return render(request, self.template_name, {
            'race': race,
            'profile': profile,
            'ijudges': ijudges,
            'judges': judges })
    def post(self, request, profile_uuid, race_uuid):
        race = get_object_or_404(Race, uuid=race_uuid)
        if race.race_finished==True:
            return HttpResponseForbidden("Race is already finished.")
        ijudges = JudgedEventJudge.objects.filter(race=race, human=request.user).first()
        if ijudges:
            return redirect(
                'races:judged_event_list',
                profile_uuid=profile_uuid,
                race_uuid=race_uuid,
            )
        judges = JudgedEventJudge.objects.filter(race=race)
        if len(judges) >= 3:
            return HttpResponseForbidden("Race already has 3 judges.")
        JudgedEventJudge.objects.create(
            race=race,
            human=request.user,
        )
        return redirect(
            'races:judged_event_list',
            profile_uuid=profile_uuid,
            race_uuid=race_uuid,
        )

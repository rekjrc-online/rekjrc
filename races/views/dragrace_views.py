from django.views import View
from ..models import Race, RaceDriver, RaceDragRace
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth.mixins import LoginRequiredMixin
from posts.models import Post
from django.db.models import Max
import random
import math

class RaceDragRaceView(LoginRequiredMixin, View):
    template_name = "races/race_drag_race.html"

    def get(self, request, profile_uuid, race_uuid):
        race = get_object_or_404(Race, uuid=race_uuid)
        if race.race_finished==True:
            print(1)
            return redirect("profiles:detail-profile", profile_uuid=profile_uuid)

        if race.human != request.user:
            print(2)
            return redirect("profiles:detail-profile", profile_uuid=profile_uuid)

        print(3)
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

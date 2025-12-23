from django.core.exceptions import ValidationError
from django.db import models
from rekjrc.base_models import BaseModel
from clubs.models import Club
from events.models import Event
from humans.models import Human
from locations.models import Location
from profiles.models import Profile
from teams.models import Team
from tracks.models import Track
from django.core.validators import MinValueValidator, MaxValueValidator

class Race(BaseModel):
    RACE_TYPE_CHOICES = [
        ('Lap Race',        'Lap Race'),
        ('Drag Race',       'Drag Race'),
        ('Crawler Comp',    'Crawler Comp'),
        ('Stopwatch Race',  'Stopwatch Race'),
        ('Long Jump',       'Long Jump'),
        ('Top Speed',       'Top Speed'),
        ('Judged Event',    'Judged Event')
    ]
    race_type = models.CharField(
        max_length=30,
        choices=RACE_TYPE_CHOICES,
        default='')
    human = models.ForeignKey(
        Human,
        on_delete=models.CASCADE,
        related_name='races',
        db_index=True,
        null=True,
        blank=True)
    profile = models.OneToOneField(
        Profile,
        on_delete=models.CASCADE,
        db_index=True,
        related_name='race',
        default=1)
    event = models.ForeignKey(
        Event,
        on_delete=models.SET_NULL,
        related_name='races',
        db_index=True,
        null=True,
        blank=True)
    location = models.ForeignKey(
        Location,
        on_delete=models.SET_NULL,
        related_name='races',
        db_index=True,
        null=True,
        blank=True)
    track = models.ForeignKey(
        Track,
        on_delete=models.SET_NULL,
        related_name='races',
        db_index=True,
        null=True,
        blank=True)
    club = models.ForeignKey(
        Club,
        on_delete=models.SET_NULL,
        related_name='races',
        db_index=True,
        null=True,
        blank=True)
    team = models.ForeignKey(
        Team,
        on_delete=models.SET_NULL,
        related_name='races',
        db_index=True,
        null=True,
        blank=True)
    TRANSPONDER_CHOICES = [
        ('LapMonitor','LapMonitor'),
        ('MyLaps','MyLaps')]
    transponder = models.CharField(max_length=10, choices=TRANSPONDER_CHOICES, blank=True, null=True)
    entry_locked = models.BooleanField(default=False)
    race_finished = models.BooleanField(default=False)
    def __str__(self):
        return self.profile.displayname

class RaceAttributeEnum(BaseModel):
    name = models.CharField(max_length=100, unique=True)
    def __str__(self):
        return self.name

class RaceAttribute(BaseModel):
    race = models.ForeignKey(
        Race,
        on_delete=models.CASCADE,
        related_name='attributes',
        db_index=True,
        null=True,
        blank=True)
    attribute = models.ForeignKey(
        RaceAttributeEnum,
        on_delete=models.CASCADE,
        related_name='race_attributes')
    value = models.CharField(max_length=255)
    class Meta:
        unique_together = ('race', 'attribute')
    def __str__(self):
        return f"{self.race}: {self.attribute.name} = {self.value}"

class LapMonitorResult(BaseModel):
    race = models.ForeignKey(
        Race,
        on_delete=models.CASCADE,
        related_name='lapmonitor_results',
        db_index=True)
    session_id = models.UUIDField()
    session_name = models.CharField(max_length=100)
    session_date = models.DateTimeField()
    session_kind = models.CharField(max_length=50)
    session_duration = models.FloatField()
    driver_id = models.UUIDField()
    driver_name = models.CharField(max_length=100)
    driver_transponder_id = models.CharField(max_length=50)
    driver_rank = models.IntegerField()
    lap_index = models.IntegerField()
    lap_end_time = models.FloatField()
    lap_duration = models.FloatField()
    lap_kind = models.CharField(max_length=50)
    class Meta:
        verbose_name = "LapMonitor Result"
        verbose_name_plural = "LapMonitor Results"
        indexes = [
            models.Index(fields=["session_id"]),
            models.Index(fields=["driver_id"]),
            models.Index(fields=["race", "session_id", "driver_id", "lap_index"])]
    def __str__(self):
        return f"{self.session_name} - {self.driver_name} (Lap {self.lap_index})"

class RaceDriver(BaseModel):
    race = models.ForeignKey(
        Race,
        on_delete=models.CASCADE,
        related_name='race_drivers')
    human = models.ForeignKey(
        Human,
        on_delete=models.CASCADE,
        related_name='race_humans')
    driver = models.ForeignKey(
        Profile,
        on_delete=models.CASCADE,
        related_name='driver_races',
        null=True,
        blank=True,
        limit_choices_to={'profiletype':'DRIVER'})
    model = models.ForeignKey(
        Profile,
        on_delete=models.CASCADE,
        related_name='model_races',
        null=True,
        blank=True,
        limit_choices_to={'profiletype':'MODEL'})
    transponder = models.CharField(max_length=10, blank=True, null=True)
    class Meta:
        constraints = [models.UniqueConstraint(fields=['race', 'model'], name='unique_race_model')]
    def __str__(self):
        driver_name = self.driver.displayname if self.driver else '-driver-'
        model_name = self.model.displayname if self.model else '-model-'
        return f"Driver: {driver_name} - Model: {model_name}"

class RaceDragRace(BaseModel):
    round_number = models.PositiveSmallIntegerField()
    race = models.ForeignKey(
        Race,
        on_delete=models.CASCADE,
        related_name='race_rounds',
        db_index=True)
    model1 = models.ForeignKey(
        'RaceDriver',
        on_delete=models.CASCADE,
        related_name='lane1_races')
    model2 = models.ForeignKey(
        'RaceDriver',
        on_delete=models.CASCADE,
        related_name='lane2_races',
        null=True,
        blank=True)
    winner = models.ForeignKey(
        'RaceDriver',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='won_rounds')
    def __str__(self):
        return f"Round {self.round_number}: {self.model1} vs {self.model2 or 'BYE'}"


class RaceCrawlerRun(models.Model):
    race = models.ForeignKey('Race', on_delete=models.CASCADE, related_name='crawler_runs')
    racedriver = models.ForeignKey('RaceDriver', on_delete=models.CASCADE, related_name='crawler_runs')
    elapsed_time = models.FloatField(null=True, blank=True)
    penalty_points = models.IntegerField(default=0)

    def total_log_points(self):
        """Return the sum of all deltas from the related CrawlerRunLog entries."""
        return self.log_entries.aggregate(models.Sum('delta'))['delta__sum'] or 0

    def __str__(self):
        if self.elapsed_time is not None:
            return f"{self.racedriver} - {self.penalty_points} points - {self.elapsed_time:.2f}s"
        return f"{self.racedriver} - No time recorded"

class CrawlerRunLog(models.Model):
    human = models.ForeignKey(
        Human,
        on_delete=models.CASCADE,
        related_name='crawler_human_run_logs')
    
    driver = models.ForeignKey(
        Profile,
        on_delete=models.CASCADE,
        related_name='crawler_driver_run_logs',
        null=True,
        blank=True,
        limit_choices_to={'profiletype':'DRIVER'})
    
    model = models.ForeignKey(
        Profile,
        on_delete=models.CASCADE,
        related_name='crawler_model_run_logs',
        null=True,
        blank=True,
        limit_choices_to={'profiletype':'MODEL'})
    
    run = models.ForeignKey(
        'RaceCrawlerRun',
        on_delete=models.CASCADE,
        related_name='log_entries')
    
    milliseconds = models.PositiveIntegerField()
    label = models.CharField(max_length=255)
    delta = models.IntegerField(default=0)
    
    class Meta:
        ordering = ['milliseconds']

    def __str__(self):
        return f"{self.milliseconds}ms - {self.label} ({self.delta:+})"

class RaceStopwatchRun(models.Model):
    race = models.ForeignKey('Race', on_delete=models.CASCADE, related_name='stopwatch_runs')
    racedriver = models.ForeignKey('RaceDriver', on_delete=models.CASCADE, related_name='stopwatch_runs')
    elapsed_time = models.FloatField(null=True, blank=True)

    def __str__(self):
        if self.elapsed_time is not None:
            return f"{self.racedriver} - {self.elapsed_time:.2f}s"
        return f"{self.racedriver} - No time recorded"

class LongJumpRun(models.Model):
    race = models.ForeignKey('Race', on_delete=models.CASCADE, related_name='longjump_runs')
    racedriver = models.ForeignKey('RaceDriver', on_delete=models.CASCADE, related_name='longjump_runs')
    feet = models.IntegerField(null=True, blank=True, validators=[MinValueValidator(0),MaxValueValidator(999),])
    inches = models.IntegerField(null=True, blank=True, validators=[MinValueValidator(0),MaxValueValidator(11),])

    @property
    def total_inches(self):
        return self.feet * 12 + self.inches

    def __str__(self):
        if self.total_inches is not None:
            return f"{self.racedriver} - {self.feet}ft {self.inches}in"
        return f"{self.racedriver} - No distance recorded"

class TopSpeedRun(models.Model):
    race = models.ForeignKey('Race', on_delete=models.CASCADE, related_name='topspeed_runs')
    racedriver = models.ForeignKey('RaceDriver', on_delete=models.CASCADE, related_name='topspeed_runs')
    topspeed = models.IntegerField(null=True, blank=True)

    def __str__(self):
        if self.topspeed is not None:
            return f"{self.racedriver} - {self.topspeed}mph"
        return f"{self.racedriver} - No top speed recorded"

class JudgedEventRun(models.Model):
    race = models.ForeignKey('Race', on_delete=models.CASCADE)
    racedriver = models.ForeignKey('RaceDriver', on_delete=models.CASCADE)

    class Meta: constraints = [models.UniqueConstraint(fields=['race', 'racedriver'], name='unique_race_racedriver')]

    def __str__(self):
        if self.scores.exists():
            avg_score = self.scores.aggregate(models.Avg('score'))['score__avg']
            return f"{self.racedriver} - {avg_score:.1f}"
        else:
            return f"{self.racedriver} - No score recorded"

class JudgedEventRunScore(models.Model):
    run = models.ForeignKey('JudgedEventRun', on_delete=models.CASCADE, related_name='scores')
    judge = models.ForeignKey('humans.Human', on_delete=models.CASCADE, related_name='race_judge_scores')
    score = models.FloatField()

    class Meta: constraints = [models.UniqueConstraint(fields=['run', 'judge'], name='unique_judge_per_run_score')]

    def __str__(self):
        return f"{self.run.racedriver} - {self.judge.human} - {self.score:.1f}"

class JudgedEventJudge(models.Model):
    race = models.ForeignKey('Race', on_delete=models.CASCADE)
    human = models.ForeignKey('humans.Human', on_delete=models.CASCADE, related_name='race_judges')

    class Meta: constraints = [models.UniqueConstraint(fields=['race', 'human'], name='unique_judge_per_race')]

    def clean(self):
        if self.race_id:
            count = JudgedEventJudge.objects.filter(race=self.race).exclude(pk=self.pk).count()
            if count >= 3:
                raise ValidationError("A race can have at most 3 judges.")

    def __str__(self):
        return self.human.first_name + " " + self.human.last_name
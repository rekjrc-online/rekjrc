from django.contrib import admin
from django.db import models
from .models import (
    Race,
    RaceAttributeEnum,
    RaceAttribute,
    LapMonitorResult,
    RaceDriver,
    RaceDragRace,
    RaceCrawlerRun,
    CrawlerRunLog,
    RaceStopwatchRun,
    JudgedEventJudge,
    JudgedEventRun,
    JudgedEventRunScore
)

@admin.register(RaceStopwatchRun)
class StopwatchRunInline(admin.ModelAdmin):
    model = RaceStopwatchRun
    extra = 1
    can_delete = True

# Inline for CrawlerRunLog within RaceCrawlerRun
class CrawlerRunLogInline(admin.TabularInline):
    model = CrawlerRunLog
    extra = 1
    readonly_fields = ('milliseconds', 'label', 'delta')
    autocomplete_fields = ['human', 'driver', 'model']
    can_delete = True

@admin.register(RaceCrawlerRun)
class RaceCrawlerRunAdmin(admin.ModelAdmin):
    list_display = (
        'race',
        'racedriver',
        'penalty_points_display',
        'elapsed_time_display',
    )
    list_filter = ('race',)
    search_fields = ('racedriver__driver__displayname', 'race__profile__displayname')
    ordering = ('race', 'racedriver')
    readonly_fields = ('penalty_points_display', 'elapsed_time_display')
    inlines = [CrawlerRunLogInline]

    @admin.display(description="Points")
    def penalty_points_display(self, obj):
        return obj.penalty_points

    @admin.display(description="Time")
    def elapsed_time_display(self, obj):
        if obj.elapsed_time is not None:
            minutes = int(obj.elapsed_time // 60)
            seconds = int(obj.elapsed_time % 60)
            hundredths = int((obj.elapsed_time % 1) * 100)
            return f"{minutes}:{str(seconds).zfill(2)}.{str(hundredths).zfill(2)}"
        return "No time recorded"

# Inline for RaceAttribute to edit directly within Race
class RaceAttributeInline(admin.TabularInline):
    model = RaceAttribute
    extra = 1
    autocomplete_fields = ['attribute']
    fields = ['attribute', 'value']

@admin.register(LapMonitorResult)
class LapMonitorResultAdmin(admin.ModelAdmin):
    list_display = ('session_name', 'driver_name', 'lap_index', 'lap_duration', 'lap_kind')
    search_fields = ('session_name', 'driver_name', 'session_id', 'driver_id')
    list_filter = ('session_kind', 'lap_kind')
    ordering = ('session_date', 'driver_name', 'lap_index')

@admin.register(Race)
class RaceAdmin(admin.ModelAdmin):
    list_display = ['id', 'profile', 'human', 'race_type', 'event', 'location', 'track', 'club', 'team', 'transponder', 'entry_locked', 'race_finished']
    list_filter = ['event', 'race_type', 'location', 'track', 'club', 'team', 'entry_locked', 'race_finished']
    search_fields = ['profile__user__username', 'human__username', 'event__name', 'entry_locked', 'race_finished']
    autocomplete_fields = ['profile', 'human', 'event', 'location', 'track', 'club', 'team']
    inlines = [RaceAttributeInline]

@admin.register(RaceAttributeEnum)
class RaceAttributeEnumAdmin(admin.ModelAdmin):
    list_display = ['name']
    search_fields = ['name']

@admin.register(RaceAttribute)
class RaceAttributeAdmin(admin.ModelAdmin):
    list_display = ['race', 'attribute', 'value']
    list_filter = ['attribute']
    search_fields = ['value', 'race__profile__user__username', 'race__event__name']
    autocomplete_fields = ['race', 'attribute']

@admin.register(RaceDriver)
class RaceDriverAdmin(admin.ModelAdmin):
    list_display = ('race', 'human_name', 'driver_name', 'model_name', 'transponder')
    list_filter = ('race',)
    search_fields = (
        'human__first_name',
        'human__last_name',
        'driver__displayname',
        'model__displayname',
        'race__profile__displayname',)

    @admin.display(description='Human')
    def human_name(self, obj):
        if obj.human:
            return f"{obj.human.first_name} {obj.human.last_name}"
        return "-human-"

    @admin.display(description='Driver')
    def driver_name(self, obj):
        return obj.driver.displayname if obj.driver else "-driver-"

    @admin.display(description='Model')
    def model_name(self, obj):
        return obj.model.displayname if obj.model else "-model-"

@admin.register(RaceDragRace)
class RaceDragRaceAdmin(admin.ModelAdmin):
    list_display = [
        'id',
        'race',
        'round_number',
        'model1',
        'model2',
        'winner',
    ]
    list_filter = ['race', 'round_number']
    search_fields = [
        'race__profile__displayname',
        'model1__displayname',
        'model2__displayname',
        'winner__displayname',
    ]
    autocomplete_fields = ['race', 'model1', 'model2', 'winner']

@admin.register(CrawlerRunLog)
class CrawlerRunLogAdmin(admin.ModelAdmin):
    list_display = ('run', 'human', 'driver', 'model', 'milliseconds', 'label', 'delta')
    
    # Filters for quick navigation
    list_filter = (
        'human',               # Filter by human
        'driver',              # Filter by driver profile
        'model',               # Filter by model profile
    )

    search_fields = (
        'run__racedriver__driver__displayname',
        'run__race__profile__displayname',
        'human__first_name',
        'human__last_name',
        'driver__displayname',
        'model__displayname',
        'label',
    )
    
    ordering = ('run', 'milliseconds')
    autocomplete_fields = ['run', 'human', 'driver', 'model']

# Inline for JudgedEventRunScore to show scores in JudgedEventRun admin
class JudgedEventRunScoreInline(admin.TabularInline):
    model = JudgedEventRunScore
    extra = 1  # How many empty forms to display
    readonly_fields = ('judge',)  # Make judge read-only if you prefer
    fields = ('judge', 'score')

@admin.register(JudgedEventRun)
class JudgedEventRunAdmin(admin.ModelAdmin):
    list_display = ('racedriver', 'race', 'average_score')
    list_filter = ('race',)
    search_fields = ('racedriver__driver__first_name', 'racedriver__driver__last_name')
    inlines = [JudgedEventRunScoreInline]

    def average_score(self, obj):
        agg = obj.scores.aggregate(models.Avg('score'))
        avg = agg['score__avg']
        return f"{avg:.1f}" if avg is not None else "No score"
    average_score.short_description = "Average Score"

@admin.register(JudgedEventRunScore)
class JudgedEventRunScoreAdmin(admin.ModelAdmin):
    list_display = ('run', 'judge', 'score')
    search_fields = ('run__racedriver__driver__first_name', 'run__racedriver__driver__last_name', 'judge__human__first_name', 'judge__human__last_name')

@admin.register(JudgedEventJudge)
class JudgedEventJudgeAdmin(admin.ModelAdmin):
    list_display = ('human', 'race')
    list_filter = ('race',)
    search_fields = ('human__first_name', 'human__last_name')
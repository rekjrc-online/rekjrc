from django.contrib import admin
from .models import Event, EventInterest

class EventInterestInline(admin.TabularInline):
    model = EventInterest
    extra = 1
    autocomplete_fields = ('human',)

@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ('profile_displayname', 'location', 'eventdate')
    list_filter = ('location',)
    search_fields = ('profile__displayname', 'location__name')
    ordering = ('-eventdate',)
    inlines = [EventInterestInline]

    def profile_displayname(self, obj):
        return obj.profile.displayname
    profile_displayname.short_description = 'Profile Display Name'

@admin.register(EventInterest)
class EventInterestAdmin(admin.ModelAdmin):
    list_display = ('event', 'human', 'note', 'created_at')
    list_filter = ('event',)
    search_fields = ('event__profile__displayname', 'human__first_name', 'human__last_name', 'note')
    ordering = ('-created_at',)
    autocomplete_fields = ('human', 'event')

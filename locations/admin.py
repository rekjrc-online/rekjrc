from django.contrib import admin
from .models import Location

@admin.register(Location)
class LocationAdmin(admin.ModelAdmin):
    list_display = ('profile', 'human', 'latitude', 'longitude')
    search_fields = (
        'profile__displayname',
        'profile__state',
        'human__username',
        'human__first_name',
        'human__last_name',
    )
    list_filter = ('profile',)
    ordering = ('profile__displayname',)

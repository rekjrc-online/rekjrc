from django.contrib import admin
from .models import TrackType, Track, TrackAttributeEnum, TrackAttribute

@admin.register(TrackType)
class TrackTypeAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)
    ordering = ('name',)

@admin.register(Track)
class TrackAdmin(admin.ModelAdmin):
    list_display = ('profile', 'track_type', 'location', 'human')
    list_filter = ('track_type', 'location')
    search_fields = (
        'profile__displayname',
        'profile__state',
        'track_type__name',
        'location__profile__displayname',
        'human__username',
        'human__first_name',
        'human__last_name',
    )
    ordering = ('profile__displayname',)

@admin.register(TrackAttributeEnum)
class TrackAttributeEnumAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)
    ordering = ('name',)

@admin.register(TrackAttribute)
class TrackAttributeAdmin(admin.ModelAdmin):
    list_display = ('track', 'attribute_type', 'value')
    list_filter = ('attribute_type', 'track')
    search_fields = (
        'track__profile__displayname',
        'attribute_type__name',
        'value',
    )
    ordering = ('track__profile__displayname',)

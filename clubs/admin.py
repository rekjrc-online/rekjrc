from django.contrib import admin
from .models import Club, ClubLocation, ClubMember

# Inline for ClubMember
class ClubMemberInline(admin.TabularInline):
    model = ClubMember
    extra = 1
    autocomplete_fields = ('human',)


@admin.register(Club)
class ClubAdmin(admin.ModelAdmin):
    list_display = ('profile', 'human')
    search_fields = (
        'profile__displayname',
        'human__username',
        'human__first_name',
        'human__last_name',
    )
    ordering = ('profile__displayname',)
    inlines = [ClubMemberInline]


@admin.register(ClubLocation)
class ClubLocationAdmin(admin.ModelAdmin):
    list_display = ('club', 'location')
    search_fields = (
        'club__profile__displayname',
        'location__id',  # use any field that exists on Location
    )
    ordering = ('club__profile__displayname', 'location__id')


@admin.register(ClubMember)
class ClubMemberAdmin(admin.ModelAdmin):
    list_display = ('club', 'human', 'role')
    search_fields = (
        'club__profile__displayname',
        'human__username',
        'human__first_name',
        'human__last_name',
        'role',
    )
    list_filter = ('club', 'role')
    ordering = ('club__profile__displayname', 'human__username')

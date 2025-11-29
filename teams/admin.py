from django.contrib import admin
from .models import Team, TeamMember

class TeamMemberInline(admin.TabularInline):
    model = TeamMember
    extra = 1
    autocomplete_fields = ('human',)
    fields = ('human', 'role')

@admin.register(Team)
class TeamAdmin(admin.ModelAdmin):
    list_display = ('profile', 'human')
    search_fields = (
        'profile__displayname',
        'profile__state',
        'human__username',
        'human__first_name',
        'human__last_name',
    )
    ordering = ('profile__displayname',)
    inlines = [TeamMemberInline]

@admin.register(TeamMember)
class TeamMemberAdmin(admin.ModelAdmin):
    list_display = ('team', 'human', 'role')
    search_fields = (
        'team__profile__displayname',
        'human__username',
        'human__first_name',
        'human__last_name',
        'role',
    )
    list_filter = ('team', 'role')
    ordering = ('team__profile__displayname', 'human__username')

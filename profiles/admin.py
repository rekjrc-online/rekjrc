from django.contrib import admin
from .models import Profile, ProfileFollows

class ProfileAdmin(admin.ModelAdmin):
    list_display = ('human', 'displayname', 'profiletype', 'city', 'state', 'follower_count', 'chat_enabled')
    search_fields = ('human__username', 'profiletype', 'displayname', 'chat_enabled')
    list_filter = ('human', 'profiletype', 'state', 'displayname', 'chat_enabled')

admin.site.register(Profile, ProfileAdmin)

@admin.register(ProfileFollows)
class ProfileFollowsAdmin(admin.ModelAdmin):
    list_display = ('human', 'profile')
    list_filter = ('human', 'profile')
    search_fields = ('human__username', 'profile__displayname')
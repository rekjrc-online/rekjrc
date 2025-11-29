from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Human, Invitation, HumanFriend, FriendRequest

class HumanAdmin(UserAdmin):
    model = Human
    fieldsets = UserAdmin.fieldsets + (
        ('Additional Info', {'fields': ('is_verified', 'last_login_ip', 'invitation_code')}),
    )
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff', 'is_verified', 'is_active', 'invitation_code')
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Additional Info', {'fields': ('first_name', 'last_name', 'email', 'is_verified', 'last_login_ip')}),
    )
admin.site.register(Human, HumanAdmin)

class InvitationsAdmin(admin.ModelAdmin):
    model = Invitation
    def from_human_full(self, obj):
        return f"{obj.from_human.username} ({obj.from_human.first_name} {obj.from_human.last_name})"
    from_human_full.short_description = "From Human"
    def to_human_full(self, obj):
        if obj.to_human:
            return f"{obj.to_human.username} ({obj.to_human.first_name} {obj.to_human.last_name})"
        return "-"
    to_human_full.short_description = "To Human"
    list_display = ('from_human_full', 'to_human_full', 'insertdate')
    list_filter = ('from_human', 'to_human')
    search_fields = ('from_human__username', 'from_human__first_name', 'from_human__last_name',
                     'to_human__username', 'to_human__first_name', 'to_human__last_name')
admin.site.register(Invitation, InvitationsAdmin)

class HumanFriendAdmin(admin.ModelAdmin):
    list_display = ('human', 'friend_human')
    search_fields = ('human__username', 'friend_human__username')
    list_filter = ('human',)
    ordering = ('human',)
admin.site.register(HumanFriend, HumanFriendAdmin)

class FriendRequestAdmin(admin.ModelAdmin):
    list_display = ('id', 'human', 'friend_human')
    search_fields = (
        'human__displayname',
        'friend_human__displayname',
        'human__user__username',
        'friend_human__user__username')
admin.site.register(FriendRequest, FriendRequestAdmin)
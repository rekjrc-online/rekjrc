from django.contrib import admin
from .models import ChatMessage


@admin.register(ChatMessage)
class ChatMessageAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "insertdate",
        "human",
        "profile",
        "channel_profile",
        "short_content",
    )

    list_filter = (
        "insertdate",
        "human",
        "profile",
        "channel_profile",
    )

    search_fields = (
        "content",
        "human__username",
        "profile__displayname",
        "channel_profile__displayname",
    )

    ordering = ("-insertdate",)

    readonly_fields = (
        "insertdate",
    )

    def short_content(self, obj):
        return (obj.content[:60] + "…") if len(obj.content) > 60 else obj.content

    short_content.short_description = "Content"

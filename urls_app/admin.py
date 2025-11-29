from django.contrib import admin
from .models import ShortURL, ClickEvent

class ClickEventInline(admin.TabularInline):
    model = ClickEvent
    extra = 0
    readonly_fields = ("clicked_at", "user_agent", "ip_address")
    can_delete = False

@admin.register(ShortURL)
class ShortURLAdmin(admin.ModelAdmin):
    list_display = (
        "code", 
        "destination_url",
        "human",
        "profile",
        "active",
        "created_at",
    )
    list_filter = ("active", "human", "profile", "created_at")
    search_fields = ("code", "destination_url", "human__username", "profile__name")
    readonly_fields = ("created_at", "updated_at")

    inlines = [ClickEventInline]

    # Speed up admin list view by prefetching related objects
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related("human", "profile")

@admin.register(ClickEvent)
class ClickEventAdmin(admin.ModelAdmin):
    list_display = ("short_url", "clicked_at", "ip_address")
    list_filter = ("clicked_at",)
    search_fields = (
        "short_url__code",
        "ip_address",
        "user_agent",
    )
    readonly_fields = ("clicked_at",)

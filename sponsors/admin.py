from django.contrib import admin
from django.db.models import Count, Max
from .models import Sponsor, SponsorClick


@admin.register(Sponsor)
class SponsorAdmin(admin.ModelAdmin):
    list_display = ('name', 'website', 'click_count', 'last_click', 'insertdate', 'deleted')
    search_fields = ('name', 'website')
    readonly_fields = ('click_count', 'last_click',)
    ordering = ['-insertdate']

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        # Annotate with click count and last click time
        return qs.annotate(
            _click_count=Count('clicks', distinct=True),
            _last_click=Max('clicks__insertdate')
        )

    def click_count(self, obj):
        return getattr(obj, '_click_count', 0)
    click_count.short_description = 'Clicks'

    def last_click(self, obj):
        val = getattr(obj, '_last_click', None)
        return val.strftime('%m/%d/%Y %H:%M') if val else '—'
    last_click.short_description = 'Last Click'


@admin.register(SponsorClick)
class SponsorClickAdmin(admin.ModelAdmin):
    list_display = ('sponsor', 'human', 'ip_address', 'insertdate')
    list_filter = ('insertdate', 'sponsor')
    search_fields = ('sponsor__name', 'human__username', 'ip_address')
    autocomplete_fields = ('sponsor', 'human')
    ordering = ['-insertdate']

from django.contrib import admin
from .models import Store

@admin.register(Store)
class StoreAdmin(admin.ModelAdmin):
    list_display = ('profile', 'human')
    search_fields = (
        'profile__displayname',
        'profile__state',
        'human__username',
        'human__first_name',
        'human__last_name',
    )
    list_filter = ('profile', 'human')
    ordering = ('profile__displayname',)

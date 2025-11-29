from django.contrib import admin
from .models import Build, BuildAttribute, BuildAttributeEnum

@admin.register(Build)
class BuildAdmin(admin.ModelAdmin):
    list_display = ('human', 'profile')
    search_fields = ('human__username',)
    list_filter = ('human__username',)

@admin.register(BuildAttribute)
class BuildAttributeAdmin(admin.ModelAdmin):
    list_display = ('build', 'attribute_type', 'value',)
    list_filter = ('attribute_type',)

@admin.register(BuildAttributeEnum)
class BuildAttributeEnumAdmin(admin.ModelAdmin):
    list_display = ('name',)
    ordering = ['name']
from django.contrib.admin import RelatedOnlyFieldListFilter
from django.contrib import admin
from .models import Post, PostLike


class PostAdmin(admin.ModelAdmin):
    list_display = (
        'human',
        'profile',
        'profile_type',
        'short_content',
        'insertdate',
        'deleted',
    )
    search_fields = (
        'human__username',
        'profile__displayname',
        'content',
    )
    list_filter = (
        ('human', RelatedOnlyFieldListFilter),
        ('profile', RelatedOnlyFieldListFilter),
        'deleted',
        'insertdate',
    )
    autocomplete_fields = ('profile', 'human')

    def human(self, obj):
        return obj.human.username
    human.short_description = 'Human'

    def profile(self, obj):
        return obj.profile.displayname
    profile.short_description = 'Profile'

    def profile_type(self, obj):
        # assumes Profile has a field called profiletype or profile_type
        return getattr(obj.profile, 'profiletype', None) or '-'
    profile_type.short_description = 'Profile Type'

    def short_content(self, obj):
        return obj.content[:50]
    short_content.short_description = 'Content'


class PostLikeAdmin(admin.ModelAdmin):
    list_display = ('post', 'human')
    search_fields = ('post__content', 'human__username')
    autocomplete_fields = ('post', 'human')
    list_filter = (
        ('post', RelatedOnlyFieldListFilter),
        ('human', RelatedOnlyFieldListFilter),
    )


admin.site.register(Post, PostAdmin)
admin.site.register(PostLike, PostLikeAdmin)

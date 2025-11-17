from urllib.parse import urlparse, parse_qs
from django.db import models
from django.conf import settings
from django.utils import timezone
from rekjrc.base_models import BaseModel
from profiles.models import Profile
from humans.models import Human
from PIL import Image

class Post(BaseModel):
    human = models.ForeignKey (
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name='posts',
        db_index=True )
    profile = models.ForeignKey (
        Profile,
        on_delete=models.PROTECT,
        related_name='posts',
        db_index=True )
    parent = models.ForeignKey (
        'self',
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name='replies' )
    content = models.TextField(max_length=200)
    image = models.ImageField(upload_to='post_images/', blank=True, null=True)
    video_url = models.URLField(blank=True, null=True)
    likes_count = models.PositiveIntegerField(default=0)
    comments_count = models.PositiveIntegerField(default=0)
    reposts_count = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"{self.profile.displayname}: {self.content[:50]}"

    @property
    def likes_count(self):
        return self.likes.count()

    @property
    def posted_date_delta(self):
        """
        Returns a human-readable string representing the time difference
        between the post's insert date and now, using the largest sensible unit.
        Examples: '12m', '3h', '5d', '3w', '6mo', '2y'
        """
        now = timezone.now()
        delta = now - self.insertdate

        seconds = delta.total_seconds()
        minutes = seconds // 60
        hours = seconds // 3600
        days = seconds // 86400
        weeks = seconds // (86400 * 7)
        months = seconds // (86400 * 30)
        years = seconds // (86400 * 365)

        if seconds < 60:
            return "just now"
        elif minutes < 60:
            return f"{int(minutes)}m"
        elif hours < 24:
            return f"{int(hours)}h"
        elif days < 7:
            return f"{int(days)}d"
        elif weeks < 5:
            return f"{int(weeks)}w"
        elif months < 12:
            return f"{int(months)}mo"
        else:
            return f"{int(years)}y"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if self.image:
            img_path = self.image.path
            img = Image.open(img_path)
            max_size = (1024, 1024)
            img.thumbnail(max_size)
            img.save(img_path, optimize=True, quality=85)

    def youtube_id(self):
        """
        Extracts the YouTube video ID if this post's video_url is a YouTube link.
        Supports normal, short, and shorts URLs.
        Returns None if not a YouTube URL.
        """
        if not self.video_url:
            return None

        parsed = urlparse(self.video_url)
        host = parsed.netloc.lower()

        if "youtube.com" in host:
            if parsed.path.startswith("/watch"):
                return parse_qs(parsed.query).get("v", [None])[0]
            elif parsed.path.startswith("/shorts/"):
                return parsed.path.split("/shorts/")[1].split("/")[0]
        elif "youtu.be" in host:
            return parsed.path.lstrip("/")

        return None

class PostLike(BaseModel):
    human = models.ForeignKey(Human, on_delete=models.PROTECT)
    post = models.ForeignKey(Post, on_delete=models.PROTECT, related_name='likes')
    class Meta:
        unique_together = ('human', 'post')
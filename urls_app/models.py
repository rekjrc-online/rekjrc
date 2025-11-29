from django.db import models
from django.conf import settings

# Assuming Profile is your existing model
from profiles.models import Profile

class ShortURL(models.Model):
    code = models.CharField(max_length=20, unique=True)
    destination_url = models.URLField()

    # Ownership
    human = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="short_urls",
    )
    profile = models.ForeignKey(
        Profile,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="short_urls",
    )

    active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.code} → {self.destination_url}"

class ClickEvent(models.Model):
    short_url = models.ForeignKey(
        ShortURL,
        on_delete=models.CASCADE,
        related_name="click_events"
    )
    clicked_at = models.DateTimeField(auto_now_add=True)
    user_agent = models.TextField(blank=True, null=True)
    ip_address = models.GenericIPAddressField(blank=True, null=True)

    def __str__(self):
        return f"Click on {self.short_url.code} at {self.clicked_at}"

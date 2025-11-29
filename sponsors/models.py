from django.db import models
from django.conf import settings
from humans.models import Human
from rekjrc.base_models import BaseModel

class Sponsor(BaseModel):
    name = models.CharField(max_length=200, unique=True)
    website = models.URLField()
    image = models.ImageField(upload_to='sponsor_images/')
    def __str__(self):
        return self.name

class SponsorClick(BaseModel):
    human = models.ForeignKey(
        Human,
        on_delete=models.DO_NOTHING,
        null=True,
        blank=True,
        related_name='sponsor_clicks')
    sponsor = models.ForeignKey(
        Sponsor,
        on_delete=models.DO_NOTHING,
        null=True,
        blank=True,
        related_name='clicks')
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    def __str__(self):
        return f"{self.human or 'Anonymous'} clicked {self.sponsor.name} on {self.insertdate:%Y-%m-%d %H:%M:%S}"

from django.db import models
from profiles.models import Profile
from rekjrc.base_models import BaseModel
from humans.models import Human

class Location(BaseModel):
    human = models.ForeignKey(
        Human,
        on_delete=models.PROTECT,
        related_name='locations')
    profile = models.ForeignKey(
        Profile,
        on_delete=models.PROTECT,
        related_name='locations')
    latitude = models.DecimalField(max_digits=20, decimal_places=15, blank=True, null=True)
    longitude = models.DecimalField(max_digits=20, decimal_places=15, blank=True, null=True)
    def __str__(self):
        return self.profile.displayname

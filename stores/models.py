from django.db import models
from humans.models import Human
from profiles.models import Profile
from rekjrc.base_models import BaseModel

class Store(BaseModel):
    human = models.ForeignKey(
        Human,
        on_delete=models.PROTECT,
        related_name='stores')
    profile = models.OneToOneField(
        Profile,
        on_delete=models.PROTECT,
        related_name='store')
    def __str__(self):
        return self.profile.displayname

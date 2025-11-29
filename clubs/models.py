from django.db import models
from rekjrc.base_models import BaseModel
from humans.models import Human
from profiles.models import Profile
from locations.models import Location

class Club(BaseModel):
    human = models.ForeignKey(
        Human,
        on_delete=models.PROTECT,
        related_name='clubs',
        null=True,
        blank=True
    )
    profile = models.OneToOneField(
        Profile,
        on_delete=models.PROTECT,
        related_name='club'   # singular, 1:1 with profile
    )

    def __str__(self):
        return self.profile.displayname


class ClubLocation(BaseModel):
    club = models.ForeignKey(
        Club,
        on_delete=models.PROTECT,
        related_name='locations'  # matches subformset key in ProfileUpdateView
    )
    location = models.ForeignKey(
        Location,
        on_delete=models.PROTECT,
        related_name='club_locations'  # meaningful name for reverse access
    )

    def __str__(self):
        return f"{self.club.profile.displayname} @ {self.location}"


class ClubMember(BaseModel):
    club = models.ForeignKey(
        Club,
        on_delete=models.PROTECT,
        related_name='members'  # already clear
    )
    human = models.ForeignKey(
        Human,
        on_delete=models.PROTECT,
        related_name='club_memberships'
    )
    role = models.CharField(max_length=100, blank=True)

    class Meta:
        unique_together = ('club', 'human')

    def __str__(self):
        role_display = f" ({self.role})" if self.role else ""
        return f"{self.human} @ {self.club}{role_display}"

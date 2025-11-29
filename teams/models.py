from django.db import models
from humans.models import Human
from profiles.models import Profile
from rekjrc.base_models import BaseModel

class Team(BaseModel):
    human = models.ForeignKey(
        Human,
        on_delete=models.PROTECT,
        related_name='teams'
    )
    profile = models.OneToOneField(
        Profile,
        on_delete=models.PROTECT,
        related_name='team'
    )
    def __str__(self):
        return self.profile.displayname

class TeamMember(BaseModel):
    team = models.ForeignKey(
        Team,
        on_delete=models.CASCADE,
        related_name='members'
    )
    human = models.ForeignKey(
        Human,
        on_delete=models.CASCADE,
        related_name='team_memberships'
    )
    role = models.CharField(max_length=100, blank=True)
    class Meta:
        unique_together = ('team', 'human')
    def __str__(self):
        role_display = f" ({self.role})" if self.role else ""
        return f"{self.human} @ {self.team}{role_display}"

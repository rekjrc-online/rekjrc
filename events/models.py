from django.db import models
from django.utils import timezone
from rekjrc.base_models import BaseModel
from locations.models import Location
from profiles.models import Profile
from humans.models import Human

class Event(BaseModel):
    human = models.ForeignKey(
        Human,
        on_delete=models.PROTECT,
        related_name='events')
    profile = models.OneToOneField(
        Profile,
        on_delete=models.PROTECT,
        related_name='events')
    location = models.ForeignKey(
        Location,
        on_delete=models.PROTECT,
        related_name='events')
    eventdate = models.DateField(default=timezone.now)
    eventtime = models.TimeField(default=timezone.now)
    eventdays = models.IntegerField(default=1)
    def __str__(self):
        return f"{self.eventdate.strftime('%a %m/%d/%y')} - {self.profile.displayname}"

class EventInterest(BaseModel):
    event = models.ForeignKey(
        Event,
        on_delete=models.PROTECT,
        related_name='interests')
    human = models.ForeignKey(
        Human,
        on_delete=models.PROTECT,
        related_name='event_interests')
    note = models.CharField(max_length=255, blank=True)  # optional note
    created_at = models.DateTimeField(auto_now_add=True)
    class Meta:
        unique_together = ('event', 'human')
    def __str__(self):
        return f"{self.human} interested in {self.event}"
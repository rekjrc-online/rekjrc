from django.core.exceptions import ValidationError
from django.dispatch import receiver
from django.db.models.signals import post_save
from django.db import models
from rekjrc.base_models import BaseModel
from humans.models import Human
from profiles.models import Profile

class Build(BaseModel):
    human = models.ForeignKey(
        Human,
        on_delete=models.CASCADE,
        related_name='builds')
    profile = models.OneToOneField(
        Profile,
        on_delete=models.CASCADE,
        related_name='builds')
    def __str__(self):
        return self.profile.displayname
    def clean(self):
        if self.profile.human != self.human:
            raise ValidationError("You can only build models you own.")
        if self.profile.profiletype != 'MODEL':
            raise ValidationError("Only profiles of type MODEL can have builds.")
    def save(self, *args, **kwargs):
            self.full_clean()
            super().save(*args, **kwargs)

@receiver(post_save, sender=Profile)
def create_build_for_profile(sender, instance, created, **kwargs):
    """
    Automatically create a Build record whenever a new Profile is created.
    """
    if created:
        Build.objects.create(
            profile=instance,
            human=instance.human
        )

class BuildAttributeEnum(BaseModel):
    name = models.CharField(max_length=100, unique=True)
    def __str__(self):
        return self.name

class BuildAttribute(BaseModel):
    build = models.ForeignKey(Build, on_delete=models.CASCADE, related_name='attributes')
    attribute_type = models.ForeignKey(BuildAttributeEnum, on_delete=models.CASCADE)
    value = models.CharField(max_length=255)
    def __str__(self):
        return f"{self.attribute_type.name}: {self.value}"

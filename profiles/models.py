from django.db import models
from django.db.models import Count
from django.conf import settings
from rekjrc.base_models import BaseModel
from humans.models import Human
from PIL import Image

class Profile(BaseModel):
	PROFILE_TYPE_CHOICES = [
        ('DRIVER', 'Driver'),
        ('MODEL', 'Model'),
		('LOCATION', 'Location'),
		('TRACK', 'Track'),
		('RACE', 'Race'),
		('CLUB', 'Club'),
		('EVENT', 'Event'),
        ('STORE', 'Store'),
		('TEAM', 'Team'),
    ]
	human = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)
	profiletype = models.CharField(max_length=30, choices=PROFILE_TYPE_CHOICES)
	displayname = models.CharField(max_length=50, default='')
	bio = models.TextField(blank=True)
	avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)
	city = models.CharField(max_length=100, blank=True)
	state = models.CharField(max_length=100, blank=True)
	website = models.URLField(blank=True)

	def __str__(self):
		return f"{self.displayname} - {self.profiletype}"

	def save(self, *args, **kwargs):
		try:
			super().save(*args, **kwargs)  # Save first to ensure the image file exists
			if self.avatar:
				img_path = self.avatar.path
				img = Image.open(img_path)
				max_size = (200, 200)
				img.thumbnail(max_size)
				img.save(img_path, optimize=True, quality=85)
		except Exception as e:
			print("Upload failed:", e)

	@property
	def follower_count(self):
		from profiles.models import ProfileFollows  # import inside to avoid circular import
		return ProfileFollows.objects.filter(profile=self).count()

class ProfileFollows(BaseModel):
    human = models.ForeignKey(
        Human,
        on_delete=models.PROTECT,
        related_name='profile_follows')
    profile = models.ForeignKey(
        Profile,
        on_delete=models.PROTECT,
        related_name='followers')

    class Meta:
        unique_together = ('human', 'profile')

    def __str__(self):
        return f"{self.human.username} → {self.profile.displayname}"

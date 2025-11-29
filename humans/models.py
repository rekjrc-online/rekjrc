from django.contrib.auth.models import AbstractUser
from django.db import models
from rekjrc.base_models import BaseModel
from phonenumber_field.modelfields import PhoneNumberField
from django.core.validators import RegexValidator

class Human(AbstractUser, BaseModel):
    email = models.EmailField(unique=True)
    phone_number = PhoneNumberField(region='US', blank=True, null=True)
    profession = models.CharField(max_length=100, blank=True, null=True)
    is_verified = models.BooleanField(default=False)
    last_login_ip = models.GenericIPAddressField(null=True, blank=True)
    invitation_code = models.CharField(
        max_length=8,
        validators=[RegexValidator(r'^\d{8}$', message="Must be exactly 8 digits.")],
        blank=True,
        null=True,
        unique=True)
    def __str__(self):
        return f"{self.first_name} {self.last_name}".strip()

class Invitation(BaseModel):
    from_human = models.ForeignKey(Human, on_delete=models.PROTECT, related_name='sent_invitations')
    to_human = models.ForeignKey(Human, on_delete=models.PROTECT, null=True, blank=True, related_name='received_invitations')
    def __str__(self):
        return f"Invitation from {self.from_human} to {self.to_human or 'unclaimed'}"

class HumanFriend(BaseModel):
    human = models.ForeignKey(Human, on_delete=models.PROTECT, related_name='friends')
    friend_human = models.ForeignKey(Human, on_delete=models.PROTECT, related_name='friend_of')
    class Meta:
        unique_together = ('human', 'friend_human')
    def __str__(self):
        return f"{self.human} ↔ {self.friend_human}"

class FriendRequest(BaseModel):
    human = models.ForeignKey(Human, on_delete=models.PROTECT, related_name='friend_requestee')
    friend_human = models.ForeignKey(Human, on_delete=models.PROTECT, related_name='friend_requestor')
    class Meta:
        unique_together = ('human', 'friend_human')
    def __str__(self):
        return f"{self.human} ↔ {self.friend_human}"

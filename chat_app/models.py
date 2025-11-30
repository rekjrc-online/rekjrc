from django.db import models
from rekjrc.base_models import BaseModel
from humans.models import Human
from profiles.models import Profile

class ChatMessage(BaseModel):
    human = models.ForeignKey(
        Human,
        on_delete=models.PROTECT,
        related_name='chat_messages')
    profile = models.ForeignKey(
        Profile,
        on_delete=models.PROTECT,
        related_name='chat_messages')
    channel_profile = models.ForeignKey(
        Profile,
        on_delete=models.PROTECT,
        related_name='chat_messages_in_channel')
    content = models.TextField()
    class Meta:
        ordering = ["insertdate"]

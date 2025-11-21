from django.db import models
from django.utils import timezone
import uuid

class BaseModelManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(deleted=False)

class BaseModel(models.Model):
    id = models.AutoField(primary_key=True)
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, db_index=True, unique=True)
    insertdate = models.DateTimeField(default=timezone.now)
    deleted = models.BooleanField(default=False)
    objects = BaseModelManager()
    all_objects = models.Manager()
    class Meta:
        abstract = True
    def soft_delete(self):
        """Mark the record as deleted instead of removing it."""
        self.deleted = True
        self.save()

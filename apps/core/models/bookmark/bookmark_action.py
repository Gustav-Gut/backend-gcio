import uuid
from django.db import models

from apps.core.models.bookmark.bookmark_external_source import ExternalSource

class Action(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    fk_external_source = models.ForeignKey(
        ExternalSource, 
        on_delete=models.CASCADE, 
        db_column='fk_external_source_id', 
        to_field='id',
        null=True
    )
    category = models.CharField(max_length=255)
    result = models.CharField(max_length=255)
    icon = models.CharField(max_length=255)
    color = models.CharField(max_length=255)
    status = models.BooleanField(default=True)
    
    class Meta:
        db_table = 'actions'
        managed = False
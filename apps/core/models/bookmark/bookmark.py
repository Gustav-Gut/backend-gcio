
import uuid
from django.db import models

from apps.core.models.bookmark.bookmark_action import Action
from apps.core.models.bookmark.bookmark_external_source import ExternalSource


class Bookmark(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    external_source = models.ForeignKey(
        ExternalSource, 
        on_delete=models.CASCADE, 
        db_column='external_source_id', 
        to_field='id',
        null=True
    )
    action = models.ForeignKey(
        Action, 
        on_delete=models.CASCADE, 
        db_column='action_id', 
        to_field='id',
        null=True
    )
    url = models.CharField(max_length=255, db_column='url')
    title = models.CharField(max_length=255, db_column='text')
    client_id = models.CharField(max_length=255)
    status = models.BooleanField(default=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)
    
    def __str__(self):
        return self.title
    
    class Meta:
        db_table = 'bookmarks'
        managed = False
import uuid
from django.db import models

class ExternalSource(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    internal_name = models.CharField(max_length=255, null=True)
    display_name = models.CharField(max_length=255, null=True)
    description = models.CharField(max_length=255, null=True)
    favicon_url = models.CharField(max_length=255, null=True)
    status = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)
    
    def __str__(self):
        return self.title
    class Meta:
        db_table = 'external_sources'
        managed = False

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
    
    class Meta:
        db_table = 'external_sources'
        managed = False

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
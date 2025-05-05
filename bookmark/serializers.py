from rest_framework import serializers
from .models import Bookmark, Action, ExternalSource

class ExternalSourceSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExternalSource
        fields = ['id', 'display_name', 'favicon_url']

class ActionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Action
        fields = ['id', 'category', 'result', 'icon', 'color', 'status']

class BookmarkSerializer(serializers.ModelSerializer):
    external_source_id = serializers.UUIDField(write_only=True, required=False)
    action_id = serializers.UUIDField(write_only=True, required=False)
    
    class Meta:
        model = Bookmark
        fields = ['id', 'url', 'title', 'client_id', 'status', 'external_source', 
                  'action', 'external_source_id', 'action_id']
        read_only_fields = ['id']
    
    def create(self, validated_data):
        external_source_id = validated_data.pop('external_source_id', None)
        action_id = validated_data.pop('action_id', None)
        
        bookmark = Bookmark(**validated_data)
        
        if external_source_id:
            bookmark.external_source_id = external_source_id
        
        if action_id:
            bookmark.action_id = action_id
        
        bookmark.save()
        return bookmark
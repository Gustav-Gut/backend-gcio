from rest_framework import serializers
from .models import Bookmark, Action, ExternalSource

class ExternalSourceSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExternalSource
        fields = ['id', 'display_name', 'favicon_url']

class ActionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Action
        fields = ['id', 'category', 'result', 'icon', 'color', 'sections', 'status']

class BookmarkSerializer(serializers.ModelSerializer):
    action = ActionSerializer(read_only=True)
    external_source = ExternalSourceSerializer(read_only=True)
    
    class Meta:
        model = Bookmark
        fields = ['id', 'url', 'title', 'client_rut', 'action', 'external_source', 'status']
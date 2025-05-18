from rest_framework import serializers
from .models import PortalTypes

class PortalTypesSerializer(serializers.ModelSerializer):
    class Meta:
        model = PortalTypes
        fields = '__all__'

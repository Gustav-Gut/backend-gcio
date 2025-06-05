# authentication/serializers.py
from rest_framework import serializers

class LoginSerializer(serializers.Serializer):
    user_rut = serializers.CharField(required=True)
    agency_id = serializers.IntegerField(required=True)
    password = serializers.CharField(write_only=True, required=True)

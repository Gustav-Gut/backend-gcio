# authentication/serializers.py
from rest_framework import serializers

class LoginSerializer(serializers.Serializer):
    rut_cliente = serializers.CharField(required=True)
    id_inmobiliaria = serializers.IntegerField(required=True)
    password = serializers.CharField(write_only=True, required=True)

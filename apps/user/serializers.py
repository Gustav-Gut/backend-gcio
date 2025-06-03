from rest_framework import serializers
from .models import User

class UserHeaderSerializer(serializers.Serializer):
    user_rut = serializers.IntegerField(required=True, error_messages={
        'required': 'El RUT es requerido',
        'invalid': 'El RUT debe ser un número válido'
    })

class UserInfoSerializer(serializers.ModelSerializer):
    name = serializers.SerializerMethodField()
    lastname = serializers.SerializerMethodField()

    def get_name(self, obj):
       return obj.name.capitalize() if obj.name else 'Usuario'

    def get_lastname(self, obj):
        return obj.lastname.capitalize() if obj.lastname else ''

    class Meta:
        model = User
        fields = ['name', 'lastname']
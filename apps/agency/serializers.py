from rest_framework import serializers
from .models import Agency

class AgencyHeaderSerializer(serializers.Serializer):
    agency_id = serializers.IntegerField(required=True, error_messages={
        'required': 'El ID de la agencia es requerido',
        'invalid': 'El ID debe ser un número válido'
    })

    def validate_agency_id(self, value):
        try:
            agency = Agency.objects.get(id=value)
            if not agency:
                raise serializers.ValidationError("Agencia no encontrada")
            return value
        except Agency.DoesNotExist:
            raise serializers.ValidationError("Agencia no encontrada")

class AgencySerializer(serializers.ModelSerializer):
    class Meta:
        model = Agency
        fields = ['id', 'name', 'url', 'bd', 'bd_tasks']
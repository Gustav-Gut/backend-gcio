from rest_framework import serializers
from .models import PersonalEvent, GeneralEvent

class EventQueryParamsSerializer(serializers.Serializer):
    year = serializers.IntegerField(required=False)
    month = serializers.IntegerField(required=False)
    start_date = serializers.DateField(required=False, format='%Y-%m-%d')
    end_date = serializers.DateField(required=False, format='%Y-%m-%d')

    def validate(self, data):
        # Si se proporcionan year y month, validar que sean válidos
        if 'year' in data and 'month' in data:
            if not (1 <= data['month'] <= 12):
                raise serializers.ValidationError("El mes debe estar entre 1 y 12")
            return data
        
        # Si se proporcionan start_date y end_date, validar que start_date no sea mayor que end_date
        if 'start_date' in data and 'end_date' in data:
            if data['start_date'] > data['end_date']:
                raise serializers.ValidationError("La fecha de inicio no puede ser mayor que la fecha de fin")
            return data
        
        # Si no se proporcionan ni year/month ni start_date/end_date, lanzar error
        if not (('year' in data and 'month' in data) or ('start_date' in data and 'end_date' in data)):
            raise serializers.ValidationError("Debe proporcionar year y month, o start_date y end_date")
        
        return data

class PersonalEventSerializer(serializers.ModelSerializer):
    description = serializers.CharField(source='detail')
    time = serializers.SerializerMethodField()
    date = serializers.SerializerMethodField()

    def get_time(self, obj):
        if obj.date:
            # Extraer la hora del datetime y formatearla como HH:MM
            return obj.date.strftime("%H:%M")
        return None

    def get_date(self, obj):
        if obj.date:
            # Extraer la fecha del datetime y formatearla como DD-MM-YYYY
            return obj.date.strftime("%d-%m-%Y")
        return None

    class Meta:
        model = PersonalEvent
        fields = ['id', 'description', 'title', 'time', 'date']

class GeneralEventSerializer(serializers.ModelSerializer):
    description = serializers.CharField(source='detail')
    time = serializers.SerializerMethodField()
    date = serializers.SerializerMethodField()

    def get_time(self, obj):
        if obj.date:
            return obj.date.strftime("%H:%M")
        return None

    def get_date(self, obj):
        if obj.date:
            return obj.date.strftime("%d-%m-%Y")
        return None

    class Meta:
        model = GeneralEvent
        fields = ['id', 'description', 'title', 'time', 'date']

class OfferExpirationSerializer(serializers.Serializer):
    duracion_oferta = serializers.IntegerField()
    id_oferta = serializers.IntegerField()
    id_producto = serializers.IntegerField()
    glosa_proyecto = serializers.CharField()
    fecha_termino = serializers.SerializerMethodField()
    aprobada = serializers.BooleanField()

    def get_fecha_termino(self, obj):
        if obj['fecha_termino']:
            return obj['fecha_termino'].strftime("%d-%m-%Y")
        return None
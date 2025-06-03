from rest_framework import serializers
from .models import PersonalEvent

class EventQueryParamsSerializer(serializers.Serializer):
    year = serializers.IntegerField(required=True)
    month = serializers.IntegerField(required=True)

    def validate_month(self, value):
        if not 1 <= value <= 12:
            raise serializers.ValidationError("The month must be between 1 and 12.")
        return value

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
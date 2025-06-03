from rest_framework.response import Response
from rest_framework import status
from .services import EventService
from .serializers import PersonalEventSerializer, EventQueryParamsSerializer
from rest_framework import viewsets
from rest_framework.decorators import action

# Create your views here.

class EventViewSet(viewsets.ViewSet):
    @action(detail=False, methods=['get'], url_path='personal')
    def get_personal_events(self, request, *args, **kwargs):
        """
        Obtiene los eventos de un usuario para un mes específico
        
        Query Params:
            year (int): Año
            month (int): Mes (1-12)
        """
        try:
            # Obtener el RUT del header
            user_rut = request.headers.get('X-User-Rut')
            if not user_rut:
                return Response(
                    {"error": "El RUT del usuario es requerido"},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Validar los parámetros de la query
            query_serializer = EventQueryParamsSerializer(data=request.query_params)
            if not query_serializer.is_valid():
                return Response(
                    {"error": query_serializer.errors},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Obtener los eventos
            eventos = EventService.personal_events(
                user_rut=int(user_rut),
                year=query_serializer.validated_data['year'],
                month=query_serializer.validated_data['month']
            )
            
            # Serializar los eventos
            serializer = PersonalEventSerializer(eventos, many=True)
            
            return Response(serializer.data)
            
        except Exception as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

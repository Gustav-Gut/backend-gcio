from django.shortcuts import render
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status
from .services import AgencyService
from .serializers import AgencySerializer, AgencyHeaderSerializer

# Create your views here.

class AgencyViewSet(viewsets.ViewSet):
    @action(detail=False, methods=['get'], url_path='info')
    def get_agency_info(self, request, *args, **kwargs):
        """
        Obtiene la información de la agencia actual
        """
        agency_id = request.headers.get('X-Agency-Id')

        # Validar el agency_id
        header_serializer = AgencyHeaderSerializer(data={'agency_id': agency_id})
        if not header_serializer.is_valid():
            return Response(
                {"error": header_serializer.errors},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Obtener la información de la agencia
        agency = AgencyService.get_info(header_serializer.validated_data['agency_id'])

        # Serializar la respuesta
        serializer = AgencySerializer(agency)
        return Response(serializer.data)

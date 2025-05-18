from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.decorators import action
from .services import SeedServices
from .serializers import PortalTypesSerializer

class SeedAPIView(viewsets.ViewSet):
    @action(detail=False, methods=['get'], url_path='recover-portal-types')
    def recover_all_portal_types(self, request):
        portal_types = SeedServices.get_portal_type(request)
        serializer = PortalTypesSerializer(portal_types, many=True)
        return Response(serializer.data)

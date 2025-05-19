from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.versioning import URLPathVersioning

from .serializers import LoginSerializer
from .services import AuthenticateService

class AuthViewSet(viewsets.ViewSet):
    versioning_class = URLPathVersioning

    @action(detail=False, methods=['post'], url_path='login')
    def login(self, request, *args, **kwargs):
        """
        Endpoint para autenticar al usuario.
        Recibe: user_rut, agency_id y password.
        Retorna: access_token, refresh_token.
        """
        serializer = LoginSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        data = serializer.validated_data
        user, error = AuthenticateService.authenticate_user_dynamic(
            user_rut=data["user_rut"],
            agency_id=data["agency_id"],
            password=data["password"]
        )
        if error:
            return Response({"detail": error}, status=status.HTTP_401_UNAUTHORIZED)
        
        access_token, refresh_token = AuthenticateService.generate_jwt(user, data["agency_id"])
        return Response({
            "access_token": access_token, 
            "refresh_token": refresh_token
            }, status=status.HTTP_200_OK)

    @action(detail=False, methods=['post'], url_path='refresh')
    def refresh(self, request, *args, **kwargs):
        """
        Endpoint para refrescar un JWT existente.
        Recibe: refresh_token
        """
        old_refresh_token = request.data.get('refresh_token')
        if not old_refresh_token:
            return Response({'detail': 'No se proporcionó refresh token.'}, status=status.HTTP_400_BAD_REQUEST)

        access_token, refresh_token, error = AuthenticateService.refresh_jwt(old_refresh_token)
        if error:
            return Response({'detail': error}, status=status.HTTP_401_UNAUTHORIZED)

        return Response({
            "access_token": access_token, 
            "refresh_token": refresh_token
            }, status=status.HTTP_200_OK)

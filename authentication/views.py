from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenRefreshView, TokenVerifyView
from .serializers import LoginSerializer
from .services import AuthenticateService

class AuthViewSet(viewsets.ViewSet):
    @action(detail=False, methods=['post'], url_path='login')
    def login(self, request):
        """
        Endpoint para autenticar al usuario.
        Recibe: rut_cliente, id_inmobiliaria y password.
        Retorna: tokens refresh y access.
        """
        serializer = LoginSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        data = serializer.validated_data
        user, error = AuthenticateService.authenticate_user_dynamic(
            client_rut=data["rut_cliente"],
            agency_id=data["id_inmobiliaria"],
            password=data["password"]
        )
        if error:
            return Response({"detail": error}, status=status.HTTP_401_UNAUTHORIZED)
        
        # Genera los tokens utilizando simplejwt
        refresh = RefreshToken.for_user(user)
        return Response({
            "refresh": str(refresh),
            "access": str(refresh.access_token)
        }, status=status.HTTP_200_OK)

    @action(detail=False, methods=['post'], url_path='refresh')
    def refresh(self, request):
        """
        Endpoint para refrescar el token.
        Se delega la lógica en la vista estándar TokenRefreshView.
        """
        # Como estamos en un action, para reutilizar la vista de simplejwt,
        # extraemos la request original (tipo HttpRequest) de request._request.
        view = TokenRefreshView.as_view()
        return view(request._request)

    @action(detail=False, methods=['post'], url_path='verify')
    def verify(self, request):
        """
        Endpoint para verificar la validez de un token.
        Se delega la lógica en la vista estándar TokenVerifyView.
        """
        view = TokenVerifyView.as_view()
        return view(request._request)

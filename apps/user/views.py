from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status
from .services import UserService
from .serializers import UserInfoSerializer, UserHeaderSerializer
from .models import User

class UserViewSet(viewsets.ViewSet):

    @action(detail=False, methods=['get'], url_path='info')
    def userInfo(self, request, *args, **kwargs):
        """
        Obtiene la información del usuario actual
        """
        user_rut = request.headers.get('X-User-Rut')

        # Validar el RUT del usuario
        header_serializer = UserHeaderSerializer(data={'user_rut': user_rut})
        if not header_serializer.is_valid():
            return Response(
                {"error": header_serializer.errors},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            # Obtener la información del usuario
            user = UserService.get_info(header_serializer.validated_data['user_rut'])
            
            # Serializar la respuesta
            serializer = UserInfoSerializer(user)
            return Response(serializer.data)
            
        except User.DoesNotExist:
            return Response(
                {"error": "Usuario no encontrado"},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        
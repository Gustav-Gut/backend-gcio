from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from .services import UserService
from .serializers import UserInfoSerializer

class UserViewSet(viewsets.ViewSet):

    @action(detail=False, methods=['get'], url_path='info')
    def userInfo(self, request, *args, **kwargs):
        user_rut = request.headers.get('X-User-Rut')

        try:
            result = UserService.get_info(user_rut)
            user_info_serialized = UserInfoSerializer(result, many=True)
            return Response(user_info_serialized.data)
        except ValueError as e:
            return Response({
                'status': 'error',
                'message': str(e)
            }, status=400)
        
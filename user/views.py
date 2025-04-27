from django.shortcuts import render
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.decorators import action
from user.serializers import UserSerializer
from user.service import UserService

class UserAPIView(viewsets.ViewSet):
    @action(detail=False, methods=['get'], url_path='naturales')
    def login_view(self, request):
        all_user = UserService.get_users()
        serializer = UserSerializer(all_user, many=True)
        return Response(serializer.data)
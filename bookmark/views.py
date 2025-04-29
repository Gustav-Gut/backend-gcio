from django.shortcuts import render
from bookmark.services import (
    BookmarkValidationService,
    BookmarkRetrievalService,
    BookmarkProcessingService,
    BookmarkUpdatingService,
)
from . import schemas
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.pagination import PageNumberPagination
from .models import Bookmark,Action
from .serializers import BookmarkSerializer, ActionSerializer
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiExample
from drf_spectacular.types import OpenApiTypes

class BookmarkPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100

class BookmarkAPIView(viewsets.ViewSet):
  
    @extend_schema(**schemas.list_bookmarks_schema)
    @action(detail=False, methods=['get'], url_path='list')
    def list_bookmarks(self, request):
        user_id = request.query_params.get('user_id')
        
        # 1. Validación
        if not BookmarkValidationService.validate_user_id(user_id):
            return Response({"error": "User ID parameter is required"}, 
                        status=status.HTTP_400_BAD_REQUEST)
        
        # 2. Obtención de datos
        bookmarks = BookmarkRetrievalService.get_user_bookmarks(user_id)
        
        # 3. Procesamiento de datos
        result = BookmarkProcessingService.process_bookmarks_with_actions(bookmarks)
        
        # 4. Paginación
        paginator = BookmarkPagination()
        page = paginator.paginate_queryset(result, request)
        
        if page is not None:
            return paginator.get_paginated_response(page)
            
        return Response(result)


    @extend_schema(**schemas.create_bookmark_schema)
    @action(detail=False, methods=['post'], url_path='create')
    def create_bookmark(self, request):
        serializer = BookmarkSerializer(data=request.data)
        
        if serializer.is_valid():
            bookmark = serializer.save()
            return Response({"id": bookmark.id}, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @extend_schema(**schemas.update_bookmark_schema)
    @action(detail=False, methods=['patch'], url_path='update/(?P<id>[^/.]+)')
    def update_bookmark(self, request, id=None):
        try:
            bookmark = Bookmark.objects.get(id=id)
        except Bookmark.DoesNotExist:
            return Response({"error": "Bookmark not found"}, 
                        status=status.HTTP_404_NOT_FOUND)
        
    
        allowed_fields = ['title', 'url', 'status', 'action_id', 'external_source']
        data_to_update = {}
        
        for field in allowed_fields:
            if field in request.data:
                    data_to_update[field] = request.data[field]
        

        if not data_to_update:
            return Response(
                {"error": "No valid fields to update."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        serializer = BookmarkSerializer(bookmark, data=data_to_update, partial=True)
        
        if serializer.is_valid():
            serializer.save()
            return Response(
                {"message": "Bookmark updated successfully"},
                status=status.HTTP_200_OK
            )
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @extend_schema(**schemas.delete_bookmark_schema)
    @action(detail=False, methods=['delete'], url_path='delete/(?P<id>[^/.]+)')
    def delete_bookmark(self, request, id=None):
        """
        Realiza un soft delete de un bookmark cambiando su estado a inactivo.
        """
        success, error_msg = BookmarkUpdatingService.soft_delete_bookmark(id)
        
        if success:
            return Response(
                {"message": "Bookmark deleted successfully"},
                status=status.HTTP_200_OK
            )
        else:
            return Response(
                {"error": error_msg},
                status=status.HTTP_404_NOT_FOUND
            )
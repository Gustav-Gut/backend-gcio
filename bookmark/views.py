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
from .models import Bookmark,Action
from .serializers import BookmarkSerializer, ActionSerializer
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiExample
from .pagination import PaginationMixin



class BookmarkAPIView(viewsets.ViewSet,PaginationMixin):
    @extend_schema(**schemas.create_bookmark_schema)
    @action(detail=False, methods=['post'], url_path='create')
    def create_bookmark(self, request): 
        data = request.data.copy()
        bookmark, errors, status_code = BookmarkUpdatingService.create_bookmark(data)
        
        if bookmark:
            return Response({"id": bookmark.id}, status=status_code)
        
        return Response({"error": errors}, status=status_code)

    @extend_schema(**schemas.update_bookmark_schema)
    @action(detail=False, methods=['patch'], url_path='update/(?P<id>\\d+)')
    def update_bookmark(self, request, id=None):
        """
        Actualiza un bookmark existente con datos parciales.
        """
        try:
            numeric_id = int(id)
        except (ValueError, TypeError):
            return Response(
                {"error": "Invalid bookmark ID format. Must be a number."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        success, result, status_code = BookmarkUpdatingService.update_bookmark(numeric_id, request.data)
        
        return Response(result, status=status_code)
        
    @extend_schema(**schemas.delete_bookmark_schema)
    @action(detail=False, methods=['delete'], url_path='delete/(?P<id>\\d+)')
    def delete_bookmark(self, request, id=None):
        """
        Realiza un soft delete de un bookmark cambiando su estado a inactivo.
        """
        # Convertir ID a entero explícitamente para mayor seguridad
        try:
            numeric_id = int(id)
        except (ValueError, TypeError):
            return Response(
                {"error": "Invalid bookmark ID format. Must be a number."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        success, error_msg = BookmarkUpdatingService.soft_delete_bookmark(numeric_id)
        
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
    
    @extend_schema(**schemas.list_bookmarks_schema)
    @action(detail=False, methods=['get'], url_path='list')
    def list_bookmarks(self, request):
        """Lista bookmarks con múltiples opciones de filtrado."""
    
        success, bookmarks, error_response = BookmarkRetrievalService.retrieve_bookmarks(
            request.query_params
        )
        
        if not success:
            return error_response
        
        result = BookmarkProcessingService.process_bookmarks_with_actions(bookmarks)
        return self.paginate_results(result, request)
    
    @extend_schema(**schemas.list_bookmarks_by_source_schema)
    @action(detail=False, methods=['get'], url_path='by-source')
    def list_bookmarks_by_source(self, request):
        """Lista bookmarks por external_source_id con filtros opcionales."""
        success, bookmarks, error_response = BookmarkRetrievalService.retrieve_bookmarks(
            request.query_params,
            required_params=['external_source_id']
        )
        
        if not success:
            return error_response
        
        result = BookmarkProcessingService.process_bookmarks_with_actions(bookmarks)
        return self.paginate_results(result, request)

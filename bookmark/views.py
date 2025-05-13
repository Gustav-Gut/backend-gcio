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
    @action(detail=False, methods=['patch'], url_path='update')
    def update_bookmark(self, request, id=None):
        """
        Actualiza un bookmark existente con datos parciales.
        """
   
        bookmark_id = request.query_params.get('id')
        external_source_id = request.query_params.get('external_source_id')     
        result, status_code = BookmarkUpdatingService.update_bookmark(
            bookmark_id,external_source_id, request.data)
        
        return Response(result, status=status_code)
        
    @extend_schema(**schemas.delete_bookmark_schema)
    @action(detail=False, methods=['delete'], url_path='delete')
    def delete_bookmark(self, request,):
        """
        Realiza un soft delete de un bookmark cambiando su estado a inactivo.
        """
        id = request.query_params.get('id')
        external_source_id = request.query_params.get('external_source_id')
 
        success, message , status_code= BookmarkUpdatingService.soft_delete_bookmark(
            id, external_source_id
        )
        
        response_data = {"message": message} if success else {"error": message}
        return Response(response_data, status=status_code)
        
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

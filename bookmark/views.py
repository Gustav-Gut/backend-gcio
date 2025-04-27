from django.shortcuts import render
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.pagination import PageNumberPagination
from .models import Bookmark,Action
from .serializers import BookmarkSerializer, ActionSerializer

class BookmarkPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100

class BookmarkAPIView(viewsets.ViewSet):
  
    @action(detail=False, methods=['get'], url_path='list')
    def list_bookmarks(self, request):
        user_id = request.query_params.get('user_id')
        
        if not user_id:
            return Response({"error": "User ID parameter is required"}, 
                        status=status.HTTP_400_BAD_REQUEST)
        
      
        bookmarks = Bookmark.objects.filter(client_rut=user_id, status=1).select_related(
            'action', 'external_source'
        )
        
        result = []
        
        for bookmark in bookmarks:
            bookmark_data = BookmarkSerializer(bookmark).data
            
            if bookmark.external_source:
               
                related_actions = Action.objects.filter(
                    fk_external_source=bookmark.external_source,
                    status=1
                )
                bookmark_data['actions'] = ActionSerializer(related_actions, many=True).data
            
                if 'action' in bookmark_data:
                   del bookmark_data['action']
            else:
                return Response({"error": "No external source associated with this bookmark"}, 
                                status=status.HTTP_400_BAD_REQUEST)
            
            result.append(bookmark_data)
        
        paginator = BookmarkPagination()
        page = paginator.paginate_queryset(result, request)
        
        if page is not None:
            return paginator.get_paginated_response(page)
            
        return Response(result)


 
    @action(detail=False, methods=['post'], url_path='create')
    def create_bookmark(self, request):
        serializer = BookmarkSerializer(data=request.data)
        
        if serializer.is_valid():
            bookmark = serializer.save()
            return Response({"id": bookmark.id}, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['patch'], url_path='update/(?P<pk>[^/.]+)')
    def update_bookmark(self, request, pk=None):
        try:
            bookmark = Bookmark.objects.get(pk=pk)
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
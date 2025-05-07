import uuid
from rest_framework import status
from bookmark.models import Bookmark
from ..serializers import BookmarkSerializer  
from ..services import BookmarkValidationService# Updated relative import

class BookmarkUpdatingService:
    @staticmethod
    def create_bookmark(data):
        """
        Crea un nuevo bookmark con validación de UUIDs.     
        Returns:
            tuple: (bookmark, error_msg, status_code)
        """
        required_fields = ['client_id', 'external_source_id', 'action_id']
        is_valid, error = BookmarkValidationService.validate_required_fields(data, required_fields)
        if not is_valid:
            return None, error, 400
        
        if 'external_source_id' in data and data['external_source_id']:
            try:
                uuid.UUID(str(data['external_source_id']))
            except ValueError:
                return None, "Invalid external_source_id format. Must be a valid UUID.", 400
                
        if 'action_id' in data and data['action_id']:
            try:
                uuid.UUID(str(data['action_id']))
            except ValueError:
                return None, "Invalid action_id format. Must be a valid UUID.", 400
        
        serializer = BookmarkSerializer(data=data)
        if serializer.is_valid():
            bookmark = serializer.save()
            return bookmark, None, 201
        
        return None, serializer.errors, 400

    @staticmethod
    def filter_updateable_fields(data):
        """Filtra los campos permitidos para actualizar un bookmark"""
        allowed_fields = ['title', 'url', 'status', 'action_id', 'external_source']
        data_to_update = {}
        
        for field in allowed_fields:
            if field in data:
                data_to_update[field] = data[field]
        
        return data_to_update

    @staticmethod
    def update_bookmark(bookmark_id, data):
        """
        Actualiza un bookmark existente después de validación.
        
        Args:
            bookmark_id: ID del bookmark a actualizar
            data: Datos a actualizar
            
        Returns:
            tuple: (success, result, status_code)
                - success: Boolean indicando si la operación fue exitosa
                - result: Respuesta exitosa o mensaje de error
                - status_code: Código HTTP apropiado
        """
        
        # 1. Validar solicitud
        success, validation_result, status_code = BookmarkValidationService.validate_update_request(
            bookmark_id, data
        )
        
        if not success:
            return False, validation_result, status_code
        
        # 2. Actualizar el bookmark
        bookmark = validation_result["bookmark"]
        filtered_data = validation_result["data"]
        
        serializer = BookmarkSerializer(bookmark, data=filtered_data, partial=True)
        
        if serializer.is_valid():
            serializer.save()
            return True, {"message": "Bookmark updated successfully"}, status.HTTP_200_OK
    
         # 3. Manejar errores de validación del serializador
        return False, serializer.errors, status.HTTP_400_BAD_REQUEST
    @staticmethod
    def soft_delete_bookmark(bookmark_id):
        """Realiza un soft delete de un bookmark cambiando su estado a inactivo."""
        try:
            bookmark = Bookmark.objects.get(pk=bookmark_id)
            bookmark.status = False
            bookmark.save()
            return True, None
        except Bookmark.DoesNotExist:
            return False, "Bookmark not found"
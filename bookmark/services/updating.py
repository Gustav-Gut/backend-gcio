import uuid
from rest_framework import status

from bookmark.models import Action, Bookmark, ExternalSource  # Updated relative import
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
        
        # Validar formato del external_source_id 
        external_source_id = data.get('external_source_id')
        is_valid, error = BookmarkValidationService.validate_uuid_format(external_source_id, 'external_source_id')
        if not is_valid:
            return None, error, 400
        
        # Validar formato del action_id 
        action_id = data.get('action_id')
        is_valid, error = BookmarkValidationService.validate_uuid_format(action_id, 'action_id')
        if not is_valid:
            return None, error, 400
        
        is_valid, external_source, error = BookmarkValidationService.validate_active_status(
            ExternalSource, external_source_id, model_name="External Source"
        )
        if not is_valid:
            return None, error, 404
        
        # Validar que la acción existe y está activa
        is_valid, action, error = BookmarkValidationService.validate_active_status(
            Action, action_id, model_name="Action"
        )
        if not is_valid:
            return None, error, 404
        
         # Validar que la acción pertenece a la external_source indicada
        try:
            action = Action.objects.get(pk=action_id)
            if str(action.fk_external_source_id) != str(external_source_id):
                return None, "The action does not belong to the specified external source.", 400
        except Action.DoesNotExist:
            return None, "The specified action does not exist.", 404
        
        
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
    def update_bookmark(bookmark_id,external_source_id, data):
        """
        Actualiza un bookmark existente después de validación.
        
        Args:
            bookmark_id: ID del bookmark a actualizar
            data: Datos a actualizar
            
        Returns:
            tuple: (success, result, status_code)
                - result: Respuesta exitosa o mensaje de error
                - status_code: Código HTTP apropiado
        """
        
        # 1. Validar solicitud
        success, validation_result, status_code = BookmarkValidationService.validate_update_request(
            bookmark_id, external_source_id, data
        )
        
        if not success:
            return validation_result, status_code
        
        # 2. Actualizar el bookmark
        bookmark = validation_result["bookmark"]
        filtered_data = validation_result["data"]
        
        serializer = BookmarkSerializer(bookmark, data=filtered_data, partial=True)
        
        if serializer.is_valid():
            serializer.save()
            return {"message": "Bookmark updated successfully"}, status.HTTP_200_OK
    
         # 3. Manejar errores de validación del serializador
        return serializer.errors, status.HTTP_400_BAD_REQUEST

    @staticmethod
    def soft_delete_bookmark(bookmark_id, external_source_id):
        """
        Alterna el estado de un bookmark si pertenece a la fuente externa especificada.
        
        Args:
            bookmark_id: ID del bookmark (UUID) a modificar
            external_source_id: ID de la fuente externa (UUID) a la que debe pertenecer el bookmark
                    
        Returns:
            tuple: (success, message, status_code)
        """
        # Validar que los parámetros estén presentes
        is_valid, error = BookmarkValidationService.validate_required_fields(
            {'external_source_id': external_source_id, 'bookmark_id': bookmark_id}, 
            ['external_source_id', 'bookmark_id']
        )
        
        if not is_valid:
            return False, error, status.HTTP_400_BAD_REQUEST
        
        # Validar formato UUID para external_source_id
        is_valid, error = BookmarkValidationService.validate_uuid_format(
            external_source_id, 'external_source_id'
        )
        
        if not is_valid:
            return False, error, status.HTTP_400_BAD_REQUEST
        
        # Validar formato UUID para bookmark_id
        is_valid, error = BookmarkValidationService.validate_uuid_format(
            bookmark_id, 'bookmark_id'
        )
        
        if not is_valid:
            return False, error, status.HTTP_400_BAD_REQUEST
        
        try:
            # Buscar el bookmark que coincida con ambos criterios
            bookmark = Bookmark.objects.get(pk=bookmark_id, external_source_id=external_source_id)
            
            # Alternar el estado
            bookmark.status = not bookmark.status
            bookmark.save()
            
            message = "Bookmark activated" if bookmark.status else "Bookmark deactivated"
            return True, message, status.HTTP_200_OK
                
        except Bookmark.DoesNotExist:
            return False, "Bookmark not found or does not belong to the specified external source", status.HTTP_404_NOT_FOUND
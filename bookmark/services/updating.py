import uuid
from bookmark.models import Bookmark
from ..serializers import BookmarkSerializer  # Updated relative import

class BookmarkUpdatingService:
    @staticmethod
    def create_bookmark(data):
        """
        Crea un nuevo bookmark con validación de UUIDs.     
        Returns:
            tuple: (bookmark, error_msg, status_code)
        """

        if 'id' not in data:
            data['id'] = str(uuid.uuid4())
            u
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
    def update_bookmark(bookmark, data):
        """Actualiza un bookmark con los datos filtrados"""
        serializer = BookmarkSerializer(bookmark, data=data, partial=True)
        
        if serializer.is_valid():
            updated_bookmark = serializer.save()
            return updated_bookmark, None
        else:
            return None, serializer.errors
    @staticmethod
    def soft_delete_bookmark(bookmark_id):
        """
        Realiza un soft delete de un bookmark por su ID.
        
        Args:
            bookmark_id: ID del bookmark a eliminar
            
        Returns:
            tuple: (success, error_msg)
        """
        try:
            bookmark = Bookmark.objects.get(id=bookmark_id)
            bookmark.status = False
            bookmark.save()
            return True, None
        except Bookmark.DoesNotExist:
            return False, "Bookmark not found"
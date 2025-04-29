from bookmark.models import Bookmark
from ..serializers import BookmarkSerializer  # Updated relative import

class BookmarkUpdatingService:
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
            bookmark = Bookmark.objects.get(pk=bookmark_id)
            bookmark.status = False
            bookmark.save()
            return True, None
        except Bookmark.DoesNotExist:
            return False, "Bookmark not found"
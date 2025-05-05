from ..models import Bookmark, Action  # Updated relative import

class BookmarkRetrievalService:
    @staticmethod
    def get_user_bookmarks(user_id):
        """Obtiene los bookmarks activos del usuario"""
        return Bookmark.objects.filter(client_id=user_id, status=1).select_related(
            'action', 'external_source'
        )

    @staticmethod
    def get_actions_by_external_source(external_source):
        """Obtiene acciones relacionadas con una fuente externa"""
        return Action.objects.filter(
            fk_external_source=external_source,
            status=1
        )

    @staticmethod
    def get_bookmark_by_id(bookmark_id):
        """Obtiene un bookmark por su ID"""
        try:
            return Bookmark.objects.get(pk=bookmark_id)
        except Bookmark.DoesNotExist:
            return None

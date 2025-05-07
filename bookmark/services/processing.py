class BookmarkProcessingService:
    @staticmethod
    def process_bookmarks_with_actions(bookmarks):
        """
        Procesa bookmarks incluyendo su acción relacionada.
        
        Args:
            bookmarks: QuerySet de bookmarks a procesar
            
        Returns:
            list: Lista de bookmarks procesados con su acción
        """
        result = []  # Inicializar la lista de resultados
        
        # Verificar que bookmarks no sea None
        if bookmarks is None:
            return result
        
        for bookmark in bookmarks:
        
            bookmark_data = {
                "id": str(bookmark.id),
                "title": bookmark.title,
                "url": bookmark.url,
                "client_id": bookmark.client_id,
                "status": bookmark.status,
                "created_at": bookmark.created_at,
                "updated_at": bookmark.updated_at,
                "action": None  # Valor por defecto
            }
            
            # Agregar acción si existe
            if hasattr(bookmark, 'action') and bookmark.action:
                action = bookmark.action
                bookmark_data["action"] = {
                    "id": str(action.id),
                    "category": action.category,
                    "result": action.result,
                    "icon": action.icon,
                    "color": action.color,
                    "status": action.status
                }
            
            result.append(bookmark_data)
        
        return result
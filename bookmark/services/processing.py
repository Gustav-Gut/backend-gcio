from ..serializers import BookmarkSerializer, ActionSerializer
from ..models import Action  # Updated relative import

class BookmarkProcessingService:
    @staticmethod
    def process_bookmarks_with_actions(bookmarks):
        """Procesa bookmarks para incluir acciones relacionadas"""
        result = []
        
        # Recopilar IDs de fuentes externas para optimizar consultas
        external_source_ids = set()
        for bookmark in bookmarks:
            if bookmark.external_source:
                external_source_ids.add(bookmark.external_source.id)
        
        # Consultar todas las acciones relevantes de una vez
        all_actions = {}
        if external_source_ids:
            actions_list = Action.objects.filter(
                fk_external_source_id__in=external_source_ids,
                status=1
            )
            
            # Agrupar por external_source_id para acceso eficiente
            for action in actions_list:
                source_id = action.fk_external_source_id
                if source_id not in all_actions:
                    all_actions[source_id] = []
                all_actions[source_id].append(action)
        
        # Procesar cada bookmark
        for bookmark in bookmarks:
            bookmark_data = BookmarkSerializer(bookmark).data
            
            if bookmark.external_source:
                source_id = bookmark.external_source.id
                if source_id in all_actions:
                    related_actions = all_actions[source_id]
                    bookmark_data['actions'] = ActionSerializer(related_actions, many=True).data
                    
                    if 'action' in bookmark_data:
                        del bookmark_data['action']
                    
                    result.append(bookmark_data)
            
        return result

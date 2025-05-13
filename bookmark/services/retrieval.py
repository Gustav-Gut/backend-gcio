from bookmark.services.validation import BookmarkValidationService
from ..models import Bookmark, Action  # Updated relative import
from rest_framework import status
from rest_framework.response import Response
from ..serializers import BookmarkSerializer

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
    
    
    @staticmethod
    def get_bookmarks_by_external_source(external_source_id, filters=None):
        """
        Obtiene bookmarks filtrados por external_source_id y filtros opcionales.
        
        Returns:
            QuerySet: Bookmarks filtrados
        """
        # Filtro base con external_source_id
        query_filters = {'external_source_id': external_source_id}
        
        # Aplicar filtros adicionales si están presentes
        if filters:
            for key, value in filters.items():
                query_filters[key] = value
        
        # Realizar la consulta con los filtros
        return Bookmark.objects.filter(**query_filters).select_related(
            'action', 'external_source'
        )
    
    @staticmethod
    def retrieve_bookmarks_by_source(external_source_id, filters=None):
        """
        Obtiene bookmarks por source sin serializar (para procesamiento uniforme).
        
        Returns:
            tuple: (success, bookmarks, error_response)
        """
        try:
           
            bookmarks = BookmarkRetrievalService.get_bookmarks_by_external_source(
                external_source_id, filters
            )
            
            return True, bookmarks, None
            
        except Exception as e:
            return False, None, Response(
                {"error": f"An error occurred: {str(e)}"}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
            
    @staticmethod
    def get_filtered_bookmarks(filters=None):
        """
        Método base para obtener bookmarks aplicando múltiples filtros.
        
        Args:
            filters: Diccionario con los filtros a aplicar (client_id, external_source_id, status, action_id, etc.)
                
        Returns:
            QuerySet: Bookmarks filtrados
        """
        query_filters = {}
        
        # Aplicar todos los filtros disponibles
        if filters:
            for key, value in filters.items():
                if value is not None:  
                    query_filters[key] = value
        
        # Realizar la consulta con los filtros
        return Bookmark.objects.filter(**query_filters).select_related(
            'action', 'external_source'
        )
    @staticmethod
    def retrieve_bookmarks(query_params, required_params=None):
        """
        Método unificado para recuperar bookmarks basado en parámetros de consulta.
        
        Args:
            query_params: Parámetros de la consulta (QueryDict)
            required_params: Lista de parámetros requeridos (opcional)
            
        Returns:
            tuple: (success, result, error_response)
                - success: Boolean indicando si la operación fue exitosa
                - result: Bookmarks si success=True, mensaje de error si success=False
                - error_response: Response de error si success=False, None si success=True
        """
        try:
            # Verificar parámetros requeridos (si hay alguno)
            if required_params:
                for param in required_params:
                    value = query_params.get(param)
                    if not value or (isinstance(value, str) and not value.strip()):
                        return False, None, Response(
                            {"error": f"The '{param}' parameter is required"}, 
                            status=status.HTTP_400_BAD_REQUEST
                        )
            
            # Inicializar diccionario de filtros
            filters = {}
            
            # Procesar client_id (user_id) - opcional
            client_id = query_params.get('client_id')
            if client_id and client_id.strip():
                filters['client_id'] = client_id
            
            # Procesar external_source_id - opcional
            external_source_id = query_params.get('external_source_id')
            if external_source_id and external_source_id.strip():
                is_valid, error = BookmarkValidationService.validate_uuid_format(
                    external_source_id, 'external_source_id'
                )
                if not is_valid:
                    return False, None, Response(
                        {"error": error}, 
                        status=status.HTTP_400_BAD_REQUEST
                    )
                filters['external_source_id'] = external_source_id
            
            # Procesar status (por defecto True si no se especifica)
            status_param = query_params.get('status')
            if status_param:
                if status_param.lower() == 'true':
                    filters['status'] = True
                elif status_param.lower() == 'false':
                    filters['status'] = False
            
            # Procesar action_id - opcional
            action_id = query_params.get('action_id')
            if action_id and action_id.strip():
                is_valid, error = BookmarkValidationService.validate_uuid_format(
                    action_id, 'action_id'
                )
                if not is_valid:
                    return False, None, Response(
                        {"error": error}, 
                        status=status.HTTP_400_BAD_REQUEST
                    )
                filters['action_id'] = action_id
            
            # Obtener bookmarks usando el método existente
            bookmarks = BookmarkRetrievalService.get_filtered_bookmarks(filters)
            return True, bookmarks, None
            
        except Exception as e:
            return False, None, Response(
                {"error": f"An error occurred: {str(e)}"}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
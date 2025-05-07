import uuid
from rest_framework import status
from rest_framework.response import Response
from ..models import Bookmark

class BookmarkValidationService:
    @staticmethod
    def validate_user_id(user_id):
        """Valida si el ID de usuario es válido"""
        return user_id is not None and isinstance(user_id, str) and user_id.strip() != ""
    @staticmethod
    def validate_required_fields(data, required_fields, include_response=False):
        """
        Valida que los campos obligatorios estén presentes y no estén vacíos.
        
        Args:
            data: Diccionario con datos a validar
            required_fields: Lista de nombres de campos obligatorios
            include_response: Si True, incluye un objeto Response en caso de error
            
        Returns:
            Si include_response=False:
                tuple: (is_valid, error_message)
                    - is_valid: Boolean indicando si todos los campos obligatorios están presentes
                    - error_message: None si es válido, mensaje de error si no lo es
            Si include_response=True:
                tuple: (is_valid, data_or_response)
                    - is_valid: Boolean indicando si todos los campos obligatorios están presentes
                    - data_or_response: data original si es válido, objeto Response si hay error
        """
        for field in required_fields:
            if field not in data or data[field] is None or (isinstance(data[field], str) and data[field].strip() == ""):
                error_msg = f"The '{field}' field is required"
                
                if include_response:
                    return False, Response(
                        {"error": error_msg}, 
                        status=status.HTTP_400_BAD_REQUEST
                    )
                else:
                    return False, error_msg
        
        if include_response:
            return True, data
        else:
            return True, None
       

    @staticmethod
    def validate_uuid_format(value, field_name):
        """
        Valida que un valor tenga formato UUID válido.
        
        Args:
            value: Valor a validar
            field_name: Nombre del campo para mensajes de error
            
        Returns:
            tuple: (is_valid, error_message)
        """
        if not value:
            return True, None  # No hay valor para validar
            
        try:
            uuid.UUID(str(value))
            return True, None
        except ValueError:
            return False, f"{field_name} must be a valid UUID format"
    
    @staticmethod
    def prepare_source_filters(query_params):
        """
        Prepara y valida filtros para la búsqueda por external_source.
        Incluye filtros para category y result.
        
        Args:
            query_params: Parámetros de la petición
            
        Returns:
            tuple: (filters, is_valid, error_message)
        """
        filters = {}
        
    
        for param in ['client_id', 'status', 'action_id']:
            if param in query_params and query_params.get(param):
                value = query_params.get(param)
                
                if param == 'action_id':
                    is_valid, error = BookmarkValidationService.validate_uuid_format(value, param)
                    if not is_valid:
                        return {}, False, error
                
                # Conversión de status si es necesario
                if param == 'status' and value:
                    if isinstance(value, str):
                        value = value.lower() == 'true'
                
                filters[param] = value
        
        
        for param in ['category', 'result']:
            if param in query_params and query_params.get(param):
                filters[f'action__{param}'] = query_params.get(param)
        
        return filters, True, None

    @staticmethod
    def validate_listing_request(query_params):
        """
        Valida los parámetros de una solicitud de listado de bookmarks.
        
        Args:
            query_params: Parámetros de la petición
            
        Returns:
            tuple: (success, response)
                - success: Boolean indicando éxito
                - response: Response con error si hay fallo, None si éxito
        """
        user_id = query_params.get('user_id')
        
        if not BookmarkValidationService.validate_user_id(user_id):
            return False, Response(
                {"error": "User ID parameter is required"}, 
                status=status.HTTP_400_BAD_REQUEST
            )
            
        return True, None
    
    @staticmethod
    def validate_source_listing_request(query_params):
        """
        Valida los parámetros para listar bookmarks por fuente externa.
        Incluye validación para filtros de category y result.
        
        Args:
            query_params: Parámetros de la petición
                
        Returns:
            tuple: (success, data, response)
                - success: Boolean indicando si la validación fue exitosa
                - data: Diccionario con datos validados si success=True, None en caso contrario
                - response: Response con error si hay fallo, None si éxito
        """
        # 1. Validar que el campo external_source_id esté presente
        required_fields = ['external_source_id']
        is_valid, result = BookmarkValidationService.validate_required_fields(
            query_params, required_fields, include_response=True
        )
        
        if not is_valid:
            return False, None, result
        
        # 2. Validar formato UUID para external_source_id
        external_source_id = query_params.get('external_source_id')
        is_valid, error = BookmarkValidationService.validate_uuid_format(external_source_id, 'external_source_id')
        
        if not is_valid:
            return False, None, Response(
                {"error": error}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # 3. Preparar y validar filtros
        filters, is_valid, error = BookmarkValidationService.prepare_source_filters(query_params)
        
        if not is_valid:
            return False, None, Response(
                {"error": error}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # 4. Todo válido, retornar datos procesados
        return True, {"external_source_id": external_source_id, "filters": filters}, None
    
    @staticmethod
    def validate_bookmark_id(bookmark_id):
        """
        Valida que un ID de bookmark  exista en la base de datos.
        
        Args:
            bookmark_id: ID a validar
            
        Returns:
            tuple: (is_valid, bookmark, error_message)
                - is_valid: Boolean indicando si la validación fue exitosa
                - bookmark: Instancia del bookmark si existe, None si no
                - error_message: None si es válido, mensaje de error si no lo es
        """
    
        
        try:
            bookmark = Bookmark.objects.get(id=bookmark_id)
            return True, bookmark, None
        except Bookmark.DoesNotExist:
            return False, None, "Bookmark not found"
    
    @staticmethod
    def validate_update_data(data):
        """
        Valida y filtra los datos de actualización de un bookmark.
        
        Args:
            data: Datos de la solicitud para actualizar
            
        Returns:
            tuple: (is_valid, filtered_data, error_message)
                - is_valid: Boolean indicando si la validación fue exitosa
                - filtered_data: Datos filtrados con campos permitidos
                - error_message: None si es válido, mensaje de error si no lo es
        """
        # Definir campos permitidos
        allowed_fields = ['title', 'url', 'status', 'action_id', 'external_source_id']
        filtered_data = {}
        
        # Filtrar campos permitidos
        for field in allowed_fields:
            if field in data:
                # Validar UUIDs si corresponde
                if field in ['action_id', 'external_source_id'] and data[field]:
                    try:
                        uuid.UUID(str(data[field]))
                    except ValueError:
                        return False, None, f"Invalid {field} format. Must be a valid UUID."
                
                filtered_data[field] = data[field]
        
        # Verificar que hay al menos un campo para actualizar
        if not filtered_data:
            return False, None, "No valid fields to update"
        
        return True, filtered_data, None
    
    @staticmethod
    def validate_update_request(bookmark_id, data):
        """
        Valida una solicitud completa de actualización de bookmark.
        
        Args:
            bookmark_id: ID del bookmark a actualizar
            data: Datos de la solicitud
            
        Returns:
            tuple: (success, result, status_code)
                - success: Boolean indicando si la validación fue exitosa
                - result: Contendrá un dict con:
                    - Si success=True: {"bookmark": bookmark, "data": filtered_data}
                    - Si success=False: {"error": mensaje_error}
                - status_code: Código HTTP apropiado
        """
        # 1. Validar ID y existencia del bookmark
        is_valid, bookmark, error = BookmarkValidationService.validate_bookmark_id(bookmark_id)
        if not is_valid:
            return False, {"error": error}, status.HTTP_404_NOT_FOUND
        
        # 2. Validar datos de actualización
        is_valid, filtered_data, error = BookmarkValidationService.validate_update_data(data)
        if not is_valid:
            return False, {"error": error}, status.HTTP_400_BAD_REQUEST
        
        # 3. Retornar éxito con datos validados
        return True, {"bookmark": bookmark, "data": filtered_data}, status.HTTP_200_OK
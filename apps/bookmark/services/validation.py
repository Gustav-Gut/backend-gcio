import uuid
from apps.bookmark.models import Bookmark
from rest_framework import status
from rest_framework.response import Response


class BookmarkValidationService:

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
        allowed_fields = ['title', 'url', 'status']
        filtered_data = {}
        
        # Filtrar campos permitidos
        for field in allowed_fields:
            if field in data:
                filtered_data[field] = data[field]
        
        # Verificar que hay al menos un campo para actualizar
        if not filtered_data:
            return False, None, "No valid fields to update"
        
        return True, filtered_data, None
    
    @staticmethod
    def validate_update_request(bookmark_id,external_source_id, data):
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
        # 1. Validar que bookmark_id y external_source_id no esten vacíos
        if not bookmark_id or not external_source_id:
            return False, {"error": "Bookmark ID and External Source ID are required"}, status.HTTP_400_BAD_REQUEST   
        
        # 2. Validar formato UUID para external_source_id
        is_valid, error = BookmarkValidationService.validate_uuid_format(external_source_id, 'external_source_id')
        if not is_valid:
            return False, {"error": error}, status.HTTP_400_BAD_REQUEST
        
        is_valid, error = BookmarkValidationService.validate_uuid_format(bookmark_id, 'bookmark_id')
        if not is_valid:
            return False, {"error": error}, status.HTTP_400_BAD_REQUEST
        
        # 3. Validar ID y existencia del bookmark
        is_valid, bookmark, error = BookmarkValidationService.validate_bookmark_id(bookmark_id)
        if not is_valid:
            return False, {"error": error}, status.HTTP_404_NOT_FOUND
        
        # 4. Validar datos de actualización
        is_valid, filtered_data, error = BookmarkValidationService.validate_update_data(data)
        if not is_valid:
            return False, {"error": error}, status.HTTP_400_BAD_REQUEST
        
        # 5. validar que el bookmark pertenezca a la fuente externa
        is_valid, error, status_code = BookmarkValidationService.validate_bookmark_belongs_to_external_source(
            bookmark_id, external_source_id
        )
        if not is_valid:
            return False, {"error": error}, status_code 
        
       
        return True, {"bookmark": bookmark, "data": filtered_data}, status.HTTP_200_OK
    
    @staticmethod
    def validate_bookmark_belongs_to_external_source(bookmark_id, external_source_id):
        """
        Verifica que un bookmark pertenezca a una fuente externa específica.
        
        Args:
            bookmark_id: ID del bookmark a validar
            external_source_id: ID de la fuente externa que debería contener el bookmark
            
        Returns:
            tuple: (is_valid, error_message, status_code)
                - is_valid: Boolean indicando si la validación fue exitosa
                - error_message: Mensaje de error (None si is_valid es True)
                - status_code: Código HTTP apropiado para el error (None si is_valid es True)
        """

        try:
            # Buscar el bookmark
            bookmark = Bookmark.objects.get(pk=bookmark_id)
            
            # Verificar si pertenece a la fuente externa especificada
            if str(bookmark.external_source_id) != str(external_source_id):
                return False, "Bookmark does not belong to the specified external source", status.HTTP_403_FORBIDDEN
        
            return True, None, None
            
        except Bookmark.DoesNotExist:
            return False, "Bookmark not found", status.HTTP_404_NOT_FOUND
        except Exception as e:
            return False, f"An error occurred: {str(e)}", status.HTTP_500_INTERNAL_SERVER_ERROR

    @staticmethod
    def validate_active_status(model, identifier, id_field='id', model_name=None):
        """
        Valida que un registro exista y tenga su estado activo (status=True)
        
        Args:
            model: Modelo Django a validar
            identifier: Valor del identificador a buscar
            id_field: Campo que contiene el identificador (default: 'id')
            model_name: Nombre descriptivo para los mensajes de error
        
        Returns:
            tuple: (is_valid, model_instance, error_message)
                - is_valid: Boolean indicando si la validación fue exitosa
                - model_instance: Instancia del modelo si existe y está activo, None si no
                - error_message: None si es válido, mensaje de error si no lo es
        """
        if model_name is None:
            model_name = model.__name__
            
        try:
            # Buscar el objeto por su identificador
            filters = {id_field: identifier}
            instance = model.objects.get(**filters)
            
            # Verificar si está activo
            if hasattr(instance, 'status') and not instance.status:
                return False, None, f"The {model_name} is not active"
            
            return True, instance, None
            
        except model.DoesNotExist:
            return False, None, f"{model_name} not found"
        except Exception as e:
            return False, None, f"Error validating {model_name}: {str(e)}"
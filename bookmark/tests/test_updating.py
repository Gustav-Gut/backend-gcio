import pytest
import uuid
from unittest import mock
from rest_framework import status

from bookmark.services.updating import BookmarkUpdatingService
from bookmark.models import Bookmark


@pytest.mark.django_db
def test_create_bookmark_missing_required_fields():
    """Prueba crear bookmark cuando faltan campos requeridos"""
    data = {"client_id": "client123", "external_source_id": None}
    
    with mock.patch('bookmark.services.validation.BookmarkValidationService.validate_required_fields') as mock_validate:
        mock_validate.return_value = (False, "The 'action_id' field is required")
        
        bookmark, error, status_code = BookmarkUpdatingService.create_bookmark(data)
        
        assert bookmark is None
        assert error == "The 'action_id' field is required"
        assert status_code == 400
        mock_validate.assert_called_once()

@pytest.mark.django_db
def test_create_bookmark_invalid_external_source_id():
    """Prueba crear bookmark con external_source_id inválido"""
    data = {
        "client_id": "client123", 
        "external_source_id": "invalid-uuid",
        "action_id": str(uuid.uuid4())
    }
    
    with mock.patch('bookmark.services.validation.BookmarkValidationService.validate_required_fields') as mock_validate:
        mock_validate.return_value = (True, None)
        
        with mock.patch('bookmark.services.validation.BookmarkValidationService.validate_uuid_format') as mock_validate_uuid:
            mock_validate_uuid.return_value = (False, "Invalid external_source_id format. Must be a valid UUID.")
            
            bookmark, error, status_code = BookmarkUpdatingService.create_bookmark(data)
            
            assert bookmark is None
            assert error == "Invalid external_source_id format. Must be a valid UUID."
            assert status_code == 400

@pytest.mark.django_db
def test_create_bookmark_invalid_action_id():
    """Prueba crear bookmark con action_id inválido"""
    data = {
        "client_id": "client123", 
        "external_source_id": str(uuid.uuid4()),
        "action_id": "invalid-uuid"
    }
    
    with mock.patch('bookmark.services.validation.BookmarkValidationService.validate_required_fields') as mock_validate:
        mock_validate.return_value = (True, None)
        
        # Simular que el primer UUID es válido (external_source_id)
        with mock.patch('bookmark.services.validation.BookmarkValidationService.validate_uuid_format') as mock_validate_uuid:
            mock_validate_uuid.side_effect = [
                (True, None),  # Para external_source_id
                (False, "Invalid action_id format. Must be a valid UUID.")  # Para action_id
            ]
            
            bookmark, error, status_code = BookmarkUpdatingService.create_bookmark(data)
            
            assert bookmark is None
            assert error == "Invalid action_id format. Must be a valid UUID."
            assert status_code == 400

@pytest.mark.django_db
def test_create_bookmark_action_not_belongs_to_external_source():
    """Prueba crear bookmark cuando la acción no pertenece a la fuente externa"""
    external_source_id = str(uuid.uuid4())
    action_id = str(uuid.uuid4())
    data = {
        "client_id": "client123", 
        "external_source_id": external_source_id,
        "action_id": action_id
    }
    
    with mock.patch('bookmark.services.validation.BookmarkValidationService.validate_required_fields') as mock_validate:
        mock_validate.return_value = (True, None)
        
        # Simular que ambos UUIDs son válidos
        with mock.patch('bookmark.services.validation.BookmarkValidationService.validate_uuid_format') as mock_validate_uuid:
            mock_validate_uuid.return_value = (True, None)
            
            # Simular que la acción existe pero no pertenece a la fuente externa
            with mock.patch('bookmark.models.Action.objects.get') as mock_get_action:
                mock_action = mock.MagicMock()
                mock_action.fk_external_source_id = uuid.uuid4()  # Diferente al external_source_id
                mock_get_action.return_value = mock_action
                
                bookmark, error, status_code = BookmarkUpdatingService.create_bookmark(data)
                
                assert bookmark is None
                assert error == "The action does not belong to the specified external source."
                assert status_code == 400

@pytest.mark.django_db
def test_filter_updateable_fields():
    """Prueba que se filtren correctamente los campos actualizables"""
    # Datos con campos permitidos
    data = {
        "title": "Nuevo título",
        "url": "http://nueva-url.com",
        "status": False,
        "action_id": str(uuid.uuid4())
    }
    
    result = BookmarkUpdatingService.filter_updateable_fields(data)
    
    # Verificar que solo se incluyan los campos permitidos
    assert len(result) == 4
    assert result["title"] == "Nuevo título"
    assert result["url"] == "http://nueva-url.com"
    assert result["status"] == False
    assert result["action_id"] == data["action_id"]
    
    # Datos con campos no permitidos
    data = {
        "title": "Nuevo título",
        "campo_no_permitido": "valor"
    }
    
    result = BookmarkUpdatingService.filter_updateable_fields(data)
    
    # Verificar que solo se incluyan los campos permitidos
    assert len(result) == 1
    assert result["title"] == "Nuevo título"
    assert "campo_no_permitido" not in result

@pytest.mark.django_db
def test_soft_delete_bookmark_toggle_on():
    """Prueba activar un bookmark inactivo (toggle on)"""
    bookmark_id = str(uuid.uuid4())
    external_source_id = str(uuid.uuid4())
    
    # Mock para validar parámetros requeridos
    with mock.patch('bookmark.services.validation.BookmarkValidationService.validate_required_fields') as mock_validate_required:
        mock_validate_required.return_value = (True, None)
        
        # Mock para validar formato UUID
        with mock.patch('bookmark.services.validation.BookmarkValidationService.validate_uuid_format') as mock_validate_uuid:
            mock_validate_uuid.return_value = (True, None)
            
            # Mock para obtener el bookmark
            with mock.patch('bookmark.models.Bookmark.objects.get') as mock_get:
                # Simular un bookmark inactivo
                mock_bookmark = mock.MagicMock()
                mock_bookmark.status = False
                mock_get.return_value = mock_bookmark
                
                success, message, status_code = BookmarkUpdatingService.soft_delete_bookmark(bookmark_id, external_source_id)
                
                assert success is True
                assert message == "Bookmark activated"
                assert status_code == status.HTTP_200_OK
                mock_bookmark.save.assert_called_once()
                assert mock_bookmark.status is True  # Ahora está activo

@pytest.mark.django_db
def test_soft_delete_bookmark_toggle_off():
    """Prueba desactivar un bookmark activo (toggle off)"""
    bookmark_id = str(uuid.uuid4())
    external_source_id = str(uuid.uuid4())
    
    # Mock para validar parámetros requeridos
    with mock.patch('bookmark.services.validation.BookmarkValidationService.validate_required_fields') as mock_validate_required:
        mock_validate_required.return_value = (True, None)
        
        # Mock para validar formato UUID
        with mock.patch('bookmark.services.validation.BookmarkValidationService.validate_uuid_format') as mock_validate_uuid:
            mock_validate_uuid.return_value = (True, None)
            
            # Mock para obtener el bookmark
            with mock.patch('bookmark.models.Bookmark.objects.get') as mock_get:
                # Simular un bookmark activo
                mock_bookmark = mock.MagicMock()
                mock_bookmark.status = True
                mock_get.return_value = mock_bookmark
                
                success, message, status_code = BookmarkUpdatingService.soft_delete_bookmark(bookmark_id, external_source_id)
                
                assert success is True
                assert message == "Bookmark deactivated"
                assert status_code == status.HTTP_200_OK
                mock_bookmark.save.assert_called_once()
                assert mock_bookmark.status is False  # Ahora está inactivo

@pytest.mark.django_db
def test_soft_delete_bookmark_missing_params():
    """Prueba soft delete con parámetros faltantes"""
    bookmark_id = str(uuid.uuid4())
    external_source_id = None
    
    # Mock para validar parámetros requeridos falla
    with mock.patch('bookmark.services.validation.BookmarkValidationService.validate_required_fields') as mock_validate_required:
        mock_validate_required.return_value = (False, "External Source ID is required")
        
        success, message, status_code = BookmarkUpdatingService.soft_delete_bookmark(bookmark_id, external_source_id)
        
        assert success is False
        assert message == "External Source ID is required"
        assert status_code == status.HTTP_400_BAD_REQUEST

@pytest.mark.django_db
def test_soft_delete_bookmark_invalid_uuids():
    """Prueba soft delete con UUIDs inválidos"""
    bookmark_id = "invalid-uuid"
    external_source_id = str(uuid.uuid4())
    
    # Mock para validar parámetros requeridos
    with mock.patch('bookmark.services.validation.BookmarkValidationService.validate_required_fields') as mock_validate_required:
        mock_validate_required.return_value = (True, None)
        
        # Mock para validar formato UUID falla
        with mock.patch('bookmark.services.validation.BookmarkValidationService.validate_uuid_format') as mock_validate_uuid:
            mock_validate_uuid.side_effect = [
                (True, None),  # Para external_source_id
                (False, "Invalid bookmark_id format. Must be a valid UUID.")  # Para bookmark_id
            ]
            
            success, message, status_code = BookmarkUpdatingService.soft_delete_bookmark(bookmark_id, external_source_id)
            
            assert success is False
            assert message == "Invalid bookmark_id format. Must be a valid UUID."
            assert status_code == status.HTTP_400_BAD_REQUEST

@pytest.mark.django_db
def test_soft_delete_bookmark_not_found():
    """Prueba soft delete cuando el bookmark no existe"""
    bookmark_id = str(uuid.uuid4())
    external_source_id = str(uuid.uuid4())
    
    # Mock para validar parámetros requeridos
    with mock.patch('bookmark.services.validation.BookmarkValidationService.validate_required_fields') as mock_validate_required:
        mock_validate_required.return_value = (True, None)
        
        # Mock para validar formato UUID
        with mock.patch('bookmark.services.validation.BookmarkValidationService.validate_uuid_format') as mock_validate_uuid:
            mock_validate_uuid.return_value = (True, None)
            
            # Mock para obtener el bookmark lanza excepción
            with mock.patch('bookmark.models.Bookmark.objects.get') as mock_get:
                mock_get.side_effect = Bookmark.DoesNotExist
                
                success, message, status_code = BookmarkUpdatingService.soft_delete_bookmark(bookmark_id, external_source_id)
                
                assert success is False
                assert message == "Bookmark not found or does not belong to the specified external source"
                assert status_code == status.HTTP_404_NOT_FOUND

@pytest.mark.django_db
def test_update_bookmark_validation_failure():
    """
    Prueba el escenario donde la validación del bookmark falla.
    La función debe retornar el error de validación y el código de estado apropiado.
    """
    bookmark_id = str(uuid.uuid4())
    external_source_id = str(uuid.uuid4())
    update_data = {"title": "Nuevo título"}
    
    # Mock del servicio de validación para simular un fallo
    with mock.patch('bookmark.services.BookmarkValidationService.validate_update_request') as mock_validate:
        # Configurar un resultado fallido de la validación
        error_response = {"error": "Bookmark not found"}
        mock_validate.return_value = (False, error_response, status.HTTP_404_NOT_FOUND)
        
        # Ejecutar el método bajo prueba
        result, status_code = BookmarkUpdatingService.update_bookmark(
            bookmark_id, external_source_id, update_data
        )
        
        # Verificaciones
        assert status_code == status.HTTP_404_NOT_FOUND
        assert result == error_response
        mock_validate.assert_called_once_with(bookmark_id, external_source_id, update_data)

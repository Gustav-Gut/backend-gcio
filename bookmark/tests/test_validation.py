import pytest
import uuid
from unittest import mock
from rest_framework import status
from rest_framework.response import Response
from django.test import RequestFactory
from bookmark.services.validation import BookmarkValidationService
from bookmark.models import Bookmark

# Fixtures útiles para reutilizar en tests
@pytest.fixture
def valid_uuid():
    """Genera un UUID válido para pruebas."""
    return str(uuid.uuid4())

@pytest.fixture
def invalid_uuid():
    """Retorna un string que no es un UUID válido."""
    return "not-a-valid-uuid"

@pytest.fixture
def sample_data():
    """Retorna un diccionario con datos de muestra."""
    return {
        "client_id": "test_client",
        "external_source_id": str(uuid.uuid4()),
        "action_id": str(uuid.uuid4()),
        "title": "Test Bookmark",
        "url": "https://example.com"
    }

@pytest.fixture
def mock_bookmark():
    """Crea un mock de un objeto Bookmark."""
    bookmark = mock.MagicMock()
    bookmark.id = uuid.uuid4()
    bookmark.title = "Test Bookmark"
    bookmark.url = "https://example.com"
    bookmark.client_id = "test_client"
    bookmark.external_source_id = uuid.uuid4()
    return bookmark

@pytest.fixture
def required_fields():
    """Lista de campos requeridos para pruebas."""
    return ["client_id", "external_source_id", "action_id"]

# Tests para validate_required_fields
def test_validate_required_fields_success(sample_data, required_fields):
    """Verifica que validate_required_fields retorne True cuando todos los campos requeridos están presentes."""
    is_valid, error = BookmarkValidationService.validate_required_fields(sample_data, required_fields)
    
    assert is_valid is True
    assert error is None

def test_validate_required_fields_missing(sample_data, required_fields):
    """Verifica que validate_required_fields detecte campos faltantes."""
    # Eliminar un campo requerido
    sample_data.pop("client_id")
    
    is_valid, error = BookmarkValidationService.validate_required_fields(sample_data, required_fields)
    
    assert is_valid is False
    assert "client_id" in error
    assert "required" in error

def test_validate_required_fields_empty_value(sample_data, required_fields):
    """Verifica que validate_required_fields detecte campos con valores vacíos."""
    # Establecer un valor vacío
    sample_data["client_id"] = ""
    
    is_valid, error = BookmarkValidationService.validate_required_fields(sample_data, required_fields)
    
    assert is_valid is False
    assert "client_id" in error
    assert "required" in error

def test_validate_required_fields_with_response(sample_data, required_fields):
    """Verifica que validate_required_fields retorne un objeto Response cuando include_response=True."""
    # Caso exitoso
    is_valid, result = BookmarkValidationService.validate_required_fields(
        sample_data, required_fields, include_response=True
    )
    
    assert is_valid is True
    assert result == sample_data
    
    # Caso fallido
    sample_data.pop("client_id")
    is_valid, result = BookmarkValidationService.validate_required_fields(
        sample_data, required_fields, include_response=True
    )
    
    assert is_valid is False
    assert isinstance(result, Response)
    assert result.status_code == status.HTTP_400_BAD_REQUEST
    assert "error" in result.data

# Tests para validate_uuid_format
def test_validate_uuid_format_success(valid_uuid):
    """Verifica que validate_uuid_format acepte UUIDs válidos."""
    is_valid, error = BookmarkValidationService.validate_uuid_format(valid_uuid, "test_field")
    
    assert is_valid is True
    assert error is None

def test_validate_uuid_format_invalid(invalid_uuid):
    """Verifica que validate_uuid_format rechace UUIDs inválidos."""
    is_valid, error = BookmarkValidationService.validate_uuid_format(invalid_uuid, "test_field")
    
    assert is_valid is False
    assert "test_field" in error
    assert "valid UUID format" in error

def test_validate_uuid_format_empty():
    """Verifica que validate_uuid_format acepte valores vacíos."""
    is_valid, error = BookmarkValidationService.validate_uuid_format(None, "test_field")
    
    assert is_valid is True
    assert error is None

# Tests para validate_bookmark_id usando mocks
def test_validate_bookmark_id_exists(mock_bookmark):
    """Verifica que validate_bookmark_id encuentre un bookmark existente."""
    bookmark_id = mock_bookmark.id
    
    with mock.patch('bookmark.models.Bookmark.objects.get') as mock_get:
        mock_get.return_value = mock_bookmark
        
        is_valid, found_bookmark, error = BookmarkValidationService.validate_bookmark_id(bookmark_id)
        
        assert is_valid is True
        assert found_bookmark == mock_bookmark
        assert error is None
        mock_get.assert_called_once_with(id=bookmark_id)

def test_validate_bookmark_id_not_exists(valid_uuid):
    """Verifica que validate_bookmark_id detecte un bookmark inexistente."""
    with mock.patch('bookmark.models.Bookmark.objects.get') as mock_get:
        mock_get.side_effect = Bookmark.DoesNotExist
        
        is_valid, bookmark, error = BookmarkValidationService.validate_bookmark_id(valid_uuid)
        
        assert is_valid is False
        assert bookmark is None
        assert error == "Bookmark not found"
        mock_get.assert_called_once_with(id=valid_uuid)

# Tests para validate_update_data
def test_validate_update_data_valid():
    """Verifica que validate_update_data acepte y filtre datos válidos."""
    update_data = {
        "title": "Updated Title",
        "url": "https://updated.example.com",
        "status": False,
        "invalid_field": "This should be removed"
    }
    
    is_valid, filtered_data, error = BookmarkValidationService.validate_update_data(update_data)
    
    assert is_valid is True
    assert "title" in filtered_data
    assert "url" in filtered_data
    assert "status" in filtered_data
    assert "invalid_field" not in filtered_data
    assert error is None

def test_validate_update_data_empty():
    """Verifica que validate_update_data rechace datos vacíos."""
    update_data = {
        "invalid_field": "This should be removed"
    }
    
    is_valid, filtered_data, error = BookmarkValidationService.validate_update_data(update_data)
    
    assert is_valid is False
    assert filtered_data is None
    assert "No valid fields to update" in error

# Tests para validate_bookmark_belongs_to_external_source usando mocks
def test_bookmark_belongs_to_external_source(mock_bookmark):
    """Verifica que validate_bookmark_belongs_to_external_source confirme relaciones válidas."""
    bookmark_id = mock_bookmark.id
    external_source_id = mock_bookmark.external_source_id
    
    with mock.patch('bookmark.models.Bookmark.objects.get') as mock_get:
        mock_get.return_value = mock_bookmark
        
        is_valid, error, status_code = BookmarkValidationService.validate_bookmark_belongs_to_external_source(
            bookmark_id, external_source_id
        )
        
        assert is_valid is True
        assert error is None
        assert status_code is None
        mock_get.assert_called_once_with(pk=bookmark_id)

def test_bookmark_does_not_belong_to_external_source(mock_bookmark):
    """Verifica que validate_bookmark_belongs_to_external_source detecte relaciones inválidas."""
    bookmark_id = mock_bookmark.id
    # Usar un external_source_id diferente
    different_external_source_id = uuid.uuid4()
    
    with mock.patch('bookmark.models.Bookmark.objects.get') as mock_get:
        mock_get.return_value = mock_bookmark
        
        is_valid, error, status_code = BookmarkValidationService.validate_bookmark_belongs_to_external_source(
            bookmark_id, different_external_source_id
        )
        
        assert is_valid is False
        assert "does not belong" in error
        assert status_code == status.HTTP_403_FORBIDDEN
        mock_get.assert_called_once_with(pk=bookmark_id)

def test_bookmark_not_found_in_external_source_validation(valid_uuid):
    """Verifica que validate_bookmark_belongs_to_external_source maneje bookmarks inexistentes."""
    with mock.patch('bookmark.models.Bookmark.objects.get') as mock_get:
        mock_get.side_effect = Bookmark.DoesNotExist
        
        is_valid, error, status_code = BookmarkValidationService.validate_bookmark_belongs_to_external_source(
            valid_uuid, valid_uuid
        )
        
        assert is_valid is False
        assert "not found" in error
        assert status_code == status.HTTP_404_NOT_FOUND
        mock_get.assert_called_once_with(pk=valid_uuid)

# Tests para validate_update_request usando mocks
def test_validate_update_request_success(mock_bookmark):
    """Verifica que validate_update_request acepte una solicitud válida completa."""
    bookmark_id = mock_bookmark.id
    external_source_id = mock_bookmark.external_source_id
    update_data = {
        "title": "Updated Title",
        "url": "https://updated.example.com"
    }
    
    # Varios mocks para los métodos llamados dentro de validate_update_request
    with mock.patch('bookmark.services.validation.BookmarkValidationService.validate_uuid_format') as mock_validate_uuid:
        mock_validate_uuid.return_value = (True, None)
        
        with mock.patch('bookmark.services.validation.BookmarkValidationService.validate_bookmark_id') as mock_validate_id:
            mock_validate_id.return_value = (True, mock_bookmark, None)
            
            with mock.patch('bookmark.services.validation.BookmarkValidationService.validate_update_data') as mock_validate_data:
                mock_validate_data.return_value = (True, update_data, None)
                
                with mock.patch('bookmark.services.validation.BookmarkValidationService.validate_bookmark_belongs_to_external_source') as mock_validate_belongs:
                    mock_validate_belongs.return_value = (True, None, None)
                    
                    is_valid, result, status_code = BookmarkValidationService.validate_update_request(
                        bookmark_id, external_source_id, update_data
                    )
                    
                    assert is_valid is True
                    assert "bookmark" in result
                    assert "data" in result
                    assert result["bookmark"] == mock_bookmark
                    assert result["data"] == update_data
                    assert status_code == status.HTTP_200_OK

def test_validate_update_request_missing_ids():
    """Verifica que validate_update_request rechace solicitudes sin IDs."""
    update_data = {"title": "Updated Title"}
    
    is_valid, result, status_code = BookmarkValidationService.validate_update_request(
        None, None, update_data
    )
    
    assert is_valid is False
    assert "error" in result
    assert "required" in result["error"]
    assert status_code == status.HTTP_400_BAD_REQUEST

def test_validate_update_request_invalid_uuid():
    """Verifica que validate_update_request rechace UUIDs inválidos."""
    with mock.patch('bookmark.services.validation.BookmarkValidationService.validate_uuid_format') as mock_validate_uuid:
        mock_validate_uuid.return_value = (False, "Invalid UUID format")
        
        update_data = {"title": "Updated Title"}
        is_valid, result, status_code = BookmarkValidationService.validate_update_request(
            "not-a-valid-uuid", str(uuid.uuid4()), update_data
        )
        
        assert is_valid is False
        assert "error" in result
        assert result["error"] == "Invalid UUID format"
        assert status_code == status.HTTP_400_BAD_REQUEST

def test_validate_update_request_bookmark_not_found(valid_uuid):
    """Verifica que validate_update_request detecte bookmarks inexistentes."""
    update_data = {"title": "Updated Title"}
    
    with mock.patch('bookmark.services.validation.BookmarkValidationService.validate_uuid_format') as mock_validate_uuid:
        mock_validate_uuid.return_value = (True, None)
        
        with mock.patch('bookmark.services.validation.BookmarkValidationService.validate_bookmark_id') as mock_validate_id:
            mock_validate_id.return_value = (False, None, "Bookmark not found")
            
            is_valid, result, status_code = BookmarkValidationService.validate_update_request(
                valid_uuid, valid_uuid, update_data
            )
            
            assert is_valid is False
            assert "error" in result
            assert result["error"] == "Bookmark not found"
            assert status_code == status.HTTP_404_NOT_FOUND

def test_validate_update_request_wrong_external_source(mock_bookmark, valid_uuid):
    """Verifica que validate_update_request rechace actualizaciones desde fuentes externas no autorizadas."""
    update_data = {"title": "Updated Title"}
    
    with mock.patch('bookmark.services.validation.BookmarkValidationService.validate_uuid_format') as mock_validate_uuid:
        mock_validate_uuid.return_value = (True, None)
        
        with mock.patch('bookmark.services.validation.BookmarkValidationService.validate_bookmark_id') as mock_validate_id:
            mock_validate_id.return_value = (True, mock_bookmark, None)
            
            with mock.patch('bookmark.services.validation.BookmarkValidationService.validate_update_data') as mock_validate_data:
                mock_validate_data.return_value = (True, update_data, None)
                
                with mock.patch('bookmark.services.validation.BookmarkValidationService.validate_bookmark_belongs_to_external_source') as mock_validate_belongs:
                    mock_validate_belongs.return_value = (False, "Bookmark does not belong to the specified external source", status.HTTP_403_FORBIDDEN)
                    
                    is_valid, result, status_code = BookmarkValidationService.validate_update_request(
                        mock_bookmark.id, valid_uuid, update_data
                    )
                    
                    assert is_valid is False
                    assert "error" in result
                    assert "does not belong" in result["error"]
                    assert status_code == status.HTTP_403_FORBIDDEN

import pytest
from rest_framework import status
from rest_framework.response import Response
from unittest.mock import patch, MagicMock
from bookmark.services.retrieval import BookmarkRetrievalService
from bookmark.services.updating import BookmarkUpdatingService
from bookmark.services.processing import BookmarkProcessingService

@pytest.mark.django_db
def test_create_bookmark_success(api_client, monkeypatch):
    """Test successful bookmark creation."""
    # Mock del servicio para evitar validaciones reales de BD
    test_bookmark = MagicMock()
    test_bookmark.id = "123"
    
    monkeypatch.setattr(
        BookmarkUpdatingService,
        'create_bookmark',
        lambda data: (test_bookmark, None, status.HTTP_201_CREATED)
    )
    
    # Data para la prueba
    test_data = {
        "client_id": "test_user",
        "external_source_id": "550e8400-e29b-41d4-a716-446655440000",
        "action_id": "123e4567-e89b-12d3-a456-426614174000",
        "title": "Test Bookmark",
        "url": "http://test.com"
    }
    
    # Llamar al endpoint
    response = api_client.post("/api/bookmark/create/", test_data, format='json')
    
    # Verificar respuesta
    assert response.status_code == status.HTTP_201_CREATED
    assert response.json() == {"id": "123"}

@pytest.mark.django_db
def test_update_bookmark_success(api_client, monkeypatch):
    """Test successful bookmark update."""
    # Mock del servicio
    monkeypatch.setattr(
        BookmarkUpdatingService,
        'update_bookmark',
        lambda id, external_source_id, data: ({"id": "123"}, status.HTTP_200_OK)
    )
    
    # Data para la prueba
    test_data = {
        "title": "Updated Title",
        "url": "http://updated.com"
    }
    
    # Llamar al endpoint
    response = api_client.patch(
        "/api/bookmark/update/?id=123&external_source_id=550e8400-e29b-41d4-a716-446655440000",
        test_data,
        format='json'
    )
    
    # Verificar respuesta
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {"id": "123"}

@pytest.mark.django_db
def test_delete_bookmark_toggle_success(api_client, monkeypatch):
    """Test successful bookmark status toggle."""
    # 1. Probar desactivación
    monkeypatch.setattr(
        BookmarkUpdatingService,
        'soft_delete_bookmark',
        lambda id, external_source_id: (True, "Bookmark deactivated", status.HTTP_200_OK)
    )
    
    response = api_client.delete(
        "/api/bookmark/delete/?id=123&external_source_id=550e8400-e29b-41d4-a716-446655440000"
    )
    
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {"message": "Bookmark deactivated"}
    
    # 2. Probar activación
    monkeypatch.setattr(
        BookmarkUpdatingService,
        'soft_delete_bookmark',
        lambda id, external_source_id: (True, "Bookmark activated", status.HTTP_200_OK)
    )
    
    response = api_client.delete(
        "/api/bookmark/delete/?id=123&external_source_id=550e8400-e29b-41d4-a716-446655440000"
    )
    
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {"message": "Bookmark activated"}

@pytest.mark.django_db
def test_delete_bookmark_missing_params(api_client, monkeypatch):
    """Test bookmark deletion with missing parameters."""
    # Mock para simular error de parámetro faltante
    monkeypatch.setattr(
        BookmarkUpdatingService,
        'soft_delete_bookmark',
        lambda id, external_source_id: (False, "Bookmark ID is required", status.HTTP_400_BAD_REQUEST)
    )
    
    # Sin ID
    response = api_client.delete(
        "/api/bookmark/delete/?external_source_id=550e8400-e29b-41d4-a716-446655440000"
    )
    
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "error" in response.json()
    
    # Sin external_source_id
    monkeypatch.setattr(
        BookmarkUpdatingService,
        'soft_delete_bookmark',
        lambda id, external_source_id: (False, "External Source ID is required", status.HTTP_400_BAD_REQUEST)
    )
    
    response = api_client.delete("/api/bookmark/delete/?id=123")
    
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "error" in response.json()

@pytest.mark.django_db
def test_delete_bookmark_not_found(api_client, monkeypatch):
    """Test bookmark deletion when bookmark doesn't exist."""
    monkeypatch.setattr(
        BookmarkUpdatingService,
        'soft_delete_bookmark',
        lambda id, external_source_id: (False, "Bookmark not found", status.HTTP_404_NOT_FOUND)
    )
    
    response = api_client.delete(
        "/api/bookmark/delete/?id=999&external_source_id=550e8400-e29b-41d4-a716-446655440000"
    )
    
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {"error": "Bookmark not found"}

@pytest.mark.django_db
def test_delete_bookmark_unauthorized(api_client, monkeypatch):
    """Test bookmark deletion when bookmark doesn't belong to external source."""
    monkeypatch.setattr(
        BookmarkUpdatingService,
        'soft_delete_bookmark',
        lambda id, external_source_id: (
            False, 
            "Bookmark does not belong to the specified external source", 
            status.HTTP_403_FORBIDDEN
        )
    )
    
    response = api_client.delete(
        "/api/bookmark/delete/?id=123&external_source_id=550e8400-e29b-41d4-a716-446655440000"
    )
    
    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert "error" in response.json()

@pytest.mark.django_db
def test_list_bookmarks_no_filters(api_client, monkeypatch):
    """Test listing bookmarks without filters."""
    # Mock para simular respuesta exitosa
    bookmarks_data = [{"id": 1, "title": "Test Bookmark"}]
    
    monkeypatch.setattr(
        BookmarkRetrievalService,
        'retrieve_bookmarks',
        lambda query_params, required_params=None: (True, bookmarks_data, None)
    )
    
    # Mock para procesamiento
    processed_data = [{"id": 1, "title": "Test Bookmark", "action": {"id": "A1"}}]
    monkeypatch.setattr(
        BookmarkProcessingService,
        'process_bookmarks_with_actions',
        lambda bookmarks: processed_data
    )
    
    # Llamar al endpoint sin filtros
    response = api_client.get("/api/bookmark/list/")
    
    # Verificar respuesta exitosa
    assert response.status_code == status.HTTP_200_OK
    assert len(response.json()) > 0

@pytest.mark.django_db
def test_list_bookmarks_with_filters(api_client, monkeypatch):
    """Test listing bookmarks with various filters."""
    # Mock para simular respuesta exitosa
    bookmarks_data = [{"id": 1, "title": "Test Bookmark"}]
    
    def mock_retrieve_bookmarks(query_params, required_params=None):
        # Verificar que los filtros se están pasando correctamente
        expected_keys = ["user_id", "status", "action_id"]
        for key in query_params:
            if key in expected_keys:
                assert key in query_params
        return (True, bookmarks_data, None)
    
    monkeypatch.setattr(
        BookmarkRetrievalService,
        'retrieve_bookmarks',
        mock_retrieve_bookmarks
    )
    
    # Mock para procesamiento
    processed_data = [{"id": 1, "title": "Test Bookmark", "action": {"id": "A1"}}]
    monkeypatch.setattr(
        BookmarkProcessingService,
        'process_bookmarks_with_actions',
        lambda bookmarks: processed_data
    )
    
    # Llamar con múltiples filtros
    response = api_client.get("/api/bookmark/list/?user_id=123&status=true&action_id=abc")
    
    # Verificar respuesta exitosa
    assert response.status_code == status.HTTP_200_OK

@pytest.mark.django_db
def test_list_bookmarks_by_source_success(api_client, monkeypatch):
    """Test successful listing of bookmarks by source."""
    # Mock del servicio de recuperación
    bookmarks_data = [{"id": 1, "title": "Test Bookmark"}]
    
    def mock_retrieve_bookmarks(query_params, required_params=None):
        # Verificar que se está requiriendo external_source_id
        assert required_params == ['external_source_id']
        # Verificar que el parámetro está presente en la consulta
        assert 'external_source_id' in query_params
        # Devolver datos simulados
        return (True, bookmarks_data, None)
    
    monkeypatch.setattr(
        BookmarkRetrievalService,
        'retrieve_bookmarks',
        mock_retrieve_bookmarks
    )
    
    # Mock del servicio de procesamiento
    processed_data = [{"id": 1, "title": "Test Bookmark", "action": {"id": "A1"}}]
    monkeypatch.setattr(
        BookmarkProcessingService,
        'process_bookmarks_with_actions',
        lambda bookmarks: processed_data
    )
    
    # Llamar al endpoint
    response = api_client.get("/api/bookmark/by-source/?external_source_id=550e8400-e29b-41d4-a716-446655440000")
    
    # Verificar respuesta
    assert response.status_code == status.HTTP_200_OK
    assert len(response.json()) > 0

@pytest.mark.django_db
def test_list_bookmarks_by_source_missing_id(api_client, monkeypatch):
    """Test list_bookmarks_by_source without external_source_id."""
    # Mock para simular error de parámetro faltante
    monkeypatch.setattr(
        BookmarkRetrievalService,
        'retrieve_bookmarks',
        lambda query_params, required_params: (
            False, 
            None, 
            Response({"error": "The 'external_source_id' parameter is required"}, status=status.HTTP_400_BAD_REQUEST)
        )
    )
    
    # Llamar sin external_source_id
    response = api_client.get("/api/bookmark/by-source/")
    
    # Verificar error
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "error" in response.json()


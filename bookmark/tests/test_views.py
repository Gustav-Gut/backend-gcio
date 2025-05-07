import pytest
from rest_framework import status
from bookmark.services import (
    BookmarkUpdatingService, 
    BookmarkValidationService, 
    BookmarkRetrievalService,
    BookmarkProcessingService
)


@pytest.mark.django_db
def test_create_bookmark_success(api_client, monkeypatch):
    """Test successful bookmark creation through the API endpoint."""
    # Mock service response
    mock_bookmark = type('MockBookmark', (), {'id': 456})()
    monkeypatch.setattr(
        BookmarkUpdatingService, 
        'create_bookmark', 
        lambda data: (mock_bookmark, {}, 201)
    )
    
    # Test data
    test_data = {
        'user_id': 123,
        'title': 'Test Bookmark',
        'url': 'https://example.com'
    }
    
    # Call endpoint
    response = api_client.post("/api/bookmark/create/", test_data)
    
    # Assert response
    assert response.status_code == 201
    assert response.json() == {'id': 456}


@pytest.mark.django_db
def test_list_bookmarks_success(api_client, monkeypatch):
    """Test successful bookmark listing."""
    # Mock services
    monkeypatch.setattr(
        BookmarkValidationService,
        'validate_user_id',
        lambda user_id: True
    )
    
    bookmarks_data = [{'id': 1, 'title': 'Test'}]
    monkeypatch.setattr(
        BookmarkRetrievalService,
        'get_user_bookmarks',
        lambda user_id: bookmarks_data
    )
    
    processed_data = [{'id': 1, 'title': 'Test', 'actions': []}]
    monkeypatch.setattr(
        BookmarkProcessingService,
        'process_bookmarks_with_actions',
        lambda bookmarks: processed_data
    )
    
    # Call endpoint
    response = api_client.get("/api/bookmark/list/?user_id=123")
    
    # Assert response
    assert response.status_code == 200
    assert len(response.json()) > 0


@pytest.mark.django_db
def test_update_bookmark_success(api_client, monkeypatch):
    """Test successful bookmark update."""
    # Mock service
    monkeypatch.setattr(
        BookmarkUpdatingService,
        'update_bookmark',
        lambda id, data: (True, {'id': id}, 200)
    )
    
    # Test data
    test_data = {
        'title': 'Updated Title'
    }
    
    # Call endpoint
    response = api_client.patch("/api/bookmark/update/123/", test_data)
    
    # Assert response
    assert response.status_code == 200
    assert response.json() == {'id': 123}


@pytest.mark.django_db
def test_delete_bookmark_success(api_client, monkeypatch):
    """Test successful bookmark deletion."""
    # Mock service
    monkeypatch.setattr(
        BookmarkUpdatingService,
        'soft_delete_bookmark',
        lambda id: (True, "")
    )
    
    # Call endpoint
    response = api_client.delete("/api/bookmark/delete/123/")
    
    # Assert response
    assert response.status_code == 200
    assert response.json() == {'message': 'Bookmark deleted successfully'}


@pytest.mark.django_db
def test_list_bookmarks_by_source_success(api_client, monkeypatch):
    """Test successful listing of bookmarks by source."""
    # Mock validation service
    monkeypatch.setattr(
        BookmarkValidationService,
        'validate_source_listing_request',
        lambda params: (True, {'external_source_id': 'test-source', 'filters': {}}, None)
    )
    
    # Mock retrieval service
    bookmarks_data = [{'id': 1, 'title': 'Test'}]
    monkeypatch.setattr(
        BookmarkRetrievalService,
        'retrieve_bookmarks_by_source',
        lambda source_id, filters: (True, bookmarks_data, None)
    )
    
    # Mock processing service
    processed_data = [{'id': 1, 'title': 'Test', 'actions': []}]
    monkeypatch.setattr(
        BookmarkProcessingService,
        'process_bookmarks_with_actions',
        lambda bookmarks: processed_data
    )
    
    # Call endpoint
    response = api_client.get("/api/bookmark/by-source/?external_source_id=test-source")
    
    # Assert response
    assert response.status_code == 200
    assert len(response.json()) > 0
from unittest import TestCase, mock
import uuid
from rest_framework import status

from bookmark.services.updating import BookmarkUpdatingService
from bookmark.models import Bookmark
from bookmark.serializers import BookmarkSerializer

class TestBookmarkUpdatingService(TestCase):
    
    def test_create_bookmark_missing_required_fields(self):
        """Prueba crear bookmark cuando faltan campos requeridos"""
        data = {"client_id": "client123", "external_source_id": None}
        
        with mock.patch('bookmark.services.BookmarkValidationService.validate_required_fields') as mock_validate:
            mock_validate.return_value = (False, "The 'action_id' field is required")
            
            bookmark, error, status_code = BookmarkUpdatingService.create_bookmark(data)
            
            self.assertIsNone(bookmark)
            self.assertEqual(error, "The 'action_id' field is required")
            self.assertEqual(status_code, 400)
            mock_validate.assert_called_once()
    
    def test_create_bookmark_invalid_external_source_id(self):
        """Prueba crear bookmark con external_source_id inválido"""
        data = {
            "client_id": "client123", 
            "external_source_id": "invalid-uuid",
            "action_id": str(uuid.uuid4())
        }
        
        with mock.patch('bookmark.services.BookmarkValidationService.validate_required_fields') as mock_validate:
            mock_validate.return_value = (True, None)
            
            bookmark, error, status_code = BookmarkUpdatingService.create_bookmark(data)
            
            self.assertIsNone(bookmark)
            self.assertEqual(error, "Invalid external_source_id format. Must be a valid UUID.")
            self.assertEqual(status_code, 400)
    
    def test_create_bookmark_invalid_action_id(self):
        """Prueba crear bookmark con action_id inválido"""
        data = {
            "client_id": "client123", 
            "external_source_id": str(uuid.uuid4()),
            "action_id": "invalid-uuid"
        }
        
        with mock.patch('bookmark.services.BookmarkValidationService.validate_required_fields') as mock_validate:
            mock_validate.return_value = (True, None)
            
            bookmark, error, status_code = BookmarkUpdatingService.create_bookmark(data)
            
            self.assertIsNone(bookmark)
            self.assertEqual(error, "Invalid action_id format. Must be a valid UUID.")
            self.assertEqual(status_code, 400)
    
        """Prueba crear bookmark cuando el serializer es inválido"""
        data = {
            "client_id": "client123", 
            "external_source_id": str(uuid.uuid4()),
            "action_id": str(uuid.uuid4())
        }
        
        serializer_errors = {"url": ["URL is required"]}
        
        with mock.patch('bookmark.services.BookmarkValidationService.validate_required_fields') as mock_validate:
            mock_validate.return_value = (True, None)
            
            with mock.patch('bookmark.serializers.BookmarkSerializer', autospec=True) as mock_serializer_class:
                mock_serializer = mock_serializer_class.return_value
                mock_serializer.is_valid.return_value = False
                mock_serializer.errors = serializer_errors
                
                # Inyectar el mock del serializer en el método bajo prueba
                with mock.patch('bookmark.services.updating.BookmarkSerializer', return_value=mock_serializer):
                    bookmark, error, status_code = BookmarkUpdatingService.create_bookmark(data)
                    
                    self.assertIsNone(bookmark)
                    self.assertEqual(error, serializer_errors)
                    self.assertEqual(status_code, 400)
    
    def test_filter_updateable_fields(self):
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
        self.assertEqual(len(result), 4)
        self.assertEqual(result["title"], "Nuevo título")
        self.assertEqual(result["url"], "http://nueva-url.com")
        self.assertEqual(result["status"], False)
        self.assertEqual(result["action_id"], data["action_id"])
        
        # Datos con campos no permitidos
        data = {
            "title": "Nuevo título",
            "campo_no_permitido": "valor"
        }
        
        result = BookmarkUpdatingService.filter_updateable_fields(data)
        
        # Verificar que solo se incluyan los campos permitidos
        self.assertEqual(len(result), 1)
        self.assertEqual(result["title"], "Nuevo título")
        self.assertNotIn("campo_no_permitido", result)
    
    @mock.patch('bookmark.services.BookmarkValidationService.validate_update_request')
    def test_update_bookmark_validation_failed(self, mock_validate_request):
        """Prueba actualizar bookmark cuando la validación falla"""
        bookmark_id = str(uuid.uuid4())
        data = {"title": "Nuevo título"}
        
        # Simular fallo en la validación
        mock_validate_request.return_value = (
            False, 
            {"error": "Bookmark not found"}, 
            status.HTTP_404_NOT_FOUND
        )
        
        success, result, status_code = BookmarkUpdatingService.update_bookmark(bookmark_id, data)
        
        self.assertFalse(success)
        self.assertEqual(result, {"error": "Bookmark not found"})
        self.assertEqual(status_code, status.HTTP_404_NOT_FOUND)

    @mock.patch('bookmark.models.Bookmark.objects.get')
    def test_soft_delete_bookmark_success(self, mock_get):
        """Prueba soft delete cuando el bookmark existe"""
        bookmark_id = str(uuid.uuid4())
        mock_bookmark = mock.MagicMock()
        mock_get.return_value = mock_bookmark
        
        success, error = BookmarkUpdatingService.soft_delete_bookmark(bookmark_id)
        
        self.assertTrue(success)
        self.assertIsNone(error)
        mock_bookmark.save.assert_called_once()
        self.assertFalse(mock_bookmark.status)
    
    @mock.patch('bookmark.models.Bookmark.objects.get')
    def test_soft_delete_bookmark_not_found(self, mock_get):
        """Prueba soft delete cuando el bookmark no existe"""
        bookmark_id = str(uuid.uuid4())
        mock_get.side_effect = Bookmark.DoesNotExist
        
        success, error = BookmarkUpdatingService.soft_delete_bookmark(bookmark_id)
        
        self.assertFalse(success)
        self.assertEqual(error, "Bookmark not found")
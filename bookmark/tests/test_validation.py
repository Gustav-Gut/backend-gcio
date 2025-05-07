import uuid
from unittest import TestCase, mock
from rest_framework import status
from rest_framework.response import Response

from bookmark.services.validation import BookmarkValidationService
from bookmark.models import Bookmark


class TestBookmarkValidationService(TestCase):
    
    def test_validate_user_id(self):
        """Prueba la validación de user_id"""
        # Casos válidos
        self.assertTrue(BookmarkValidationService.validate_user_id("usuario123"))
        self.assertTrue(BookmarkValidationService.validate_user_id("12345"))
        
        # Casos inválidos
        self.assertFalse(BookmarkValidationService.validate_user_id(None))
        self.assertFalse(BookmarkValidationService.validate_user_id(""))
        self.assertFalse(BookmarkValidationService.validate_user_id("   "))
        self.assertFalse(BookmarkValidationService.validate_user_id(123))  # No es string
    
    def test_validate_required_fields(self):
        """Prueba la validación de campos requeridos"""
        # Caso válido
        data = {"campo1": "valor1", "campo2": "valor2"}
        is_valid, error = BookmarkValidationService.validate_required_fields(
            data, ["campo1", "campo2"]
        )
        self.assertTrue(is_valid)
        self.assertIsNone(error)
        
        # Caso inválido - campo faltante
        is_valid, error = BookmarkValidationService.validate_required_fields(
            data, ["campo1", "campo3"]
        )
        self.assertFalse(is_valid)
        self.assertEqual(error, "The 'campo3' field is required")
        
        # Caso inválido - campo vacío
        data = {"campo1": "valor1", "campo2": ""}
        is_valid, error = BookmarkValidationService.validate_required_fields(
            data, ["campo1", "campo2"]
        )
        self.assertFalse(is_valid)
        self.assertEqual(error, "The 'campo2' field is required")
        
        # Prueba con include_response=True
        is_valid, response = BookmarkValidationService.validate_required_fields(
            data, ["campo1", "campo2"], include_response=True
        )
        self.assertFalse(is_valid)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data, {"error": "The 'campo2' field is required"})
    
    def test_validate_uuid_format(self):
        """Prueba la validación de formato UUID"""
        # UUID válido
        valid_uuid = str(uuid.uuid4())
        is_valid, error = BookmarkValidationService.validate_uuid_format(valid_uuid, "test_field")
        self.assertTrue(is_valid)
        self.assertIsNone(error)
        
        # UUID inválido
        is_valid, error = BookmarkValidationService.validate_uuid_format("123-invalid", "test_field")
        self.assertFalse(is_valid)
        self.assertEqual(error, "test_field must be a valid UUID format")
        
        # Caso vacío (se considera válido según la implementación)
        is_valid, error = BookmarkValidationService.validate_uuid_format("", "test_field")
        self.assertTrue(is_valid)
        self.assertIsNone(error)
    
    def test_prepare_source_filters(self):
        """Prueba la preparación de filtros para consultas"""
        # Caso con filtros básicos
        query_params = {
            "client_id": "client123",
            "status": "true",
            "category": "technology"
        }
        filters, is_valid, error = BookmarkValidationService.prepare_source_filters(query_params)
        self.assertTrue(is_valid)
        self.assertIsNone(error)
        self.assertEqual(filters["client_id"], "client123")
        self.assertEqual(filters["status"], True)  # Convertido a booleano
        self.assertEqual(filters["action__category"], "technology")
        
        # Caso con action_id válido
        valid_uuid = str(uuid.uuid4())
        query_params = {"action_id": valid_uuid}
        filters, is_valid, error = BookmarkValidationService.prepare_source_filters(query_params)
        self.assertTrue(is_valid)
        self.assertIsNone(error)
        self.assertEqual(filters["action_id"], valid_uuid)
        
        # Caso con action_id inválido
        query_params = {"action_id": "invalid-uuid"}
        filters, is_valid, error = BookmarkValidationService.prepare_source_filters(query_params)
        self.assertFalse(is_valid)
        self.assertEqual(error, "action_id must be a valid UUID format")
        self.assertEqual(filters, {})
    
    def test_validate_listing_request(self):
        """Prueba la validación de solicitudes de listado"""
        # Caso válido
        success, response = BookmarkValidationService.validate_listing_request({"user_id": "user123"})
        self.assertTrue(success)
        self.assertIsNone(response)
        
        # Caso inválido - sin user_id
        success, response = BookmarkValidationService.validate_listing_request({})
        self.assertFalse(success)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data, {"error": "User ID parameter is required"})
    
    @mock.patch('bookmark.models.Bookmark.objects.get')
    def test_validate_bookmark_id(self, mock_get):
        """Prueba la validación de IDs de bookmark"""
        # Configurar el mock para simular un bookmark existente
        bookmark_id = "123"
        mock_bookmark = mock.MagicMock()
        mock_get.return_value = mock_bookmark
        
        # Caso válido
        is_valid, bookmark, error = BookmarkValidationService.validate_bookmark_id(bookmark_id)
        self.assertTrue(is_valid)
        self.assertEqual(bookmark, mock_bookmark)
        self.assertIsNone(error)
        
        # Caso inválido - bookmark no existe
        mock_get.side_effect = Bookmark.DoesNotExist
        is_valid, bookmark, error = BookmarkValidationService.validate_bookmark_id("999")
        self.assertFalse(is_valid)
        self.assertIsNone(bookmark)
        self.assertEqual(error, "Bookmark not found")
    
    def test_validate_update_data(self):
        """Prueba la validación de datos para actualización"""
        # Datos válidos
        valid_uuid = str(uuid.uuid4())
        data = {
            "title": "Nuevo título",
            "url": "https://ejemplo.com",
            "action_id": valid_uuid
        }
        is_valid, filtered_data, error = BookmarkValidationService.validate_update_data(data)
        self.assertTrue(is_valid)
        self.assertEqual(filtered_data, data)
        self.assertIsNone(error)
        
        # UUID inválido
        data = {"action_id": "invalid-uuid"}
        is_valid, filtered_data, error = BookmarkValidationService.validate_update_data(data)
        self.assertFalse(is_valid)
        self.assertIsNone(filtered_data)
        self.assertEqual(error, "Invalid action_id format. Must be a valid UUID.")
        
        # Sin datos válidos para actualizar
        data = {"campo_invalido": "valor"}
        is_valid, filtered_data, error = BookmarkValidationService.validate_update_data(data)
        self.assertFalse(is_valid)
        self.assertIsNone(filtered_data)
        self.assertEqual(error, "No valid fields to update")
    
    @mock.patch('bookmark.services.validation.BookmarkValidationService.validate_bookmark_id')
    @mock.patch('bookmark.services.validation.BookmarkValidationService.validate_update_data')
    def test_validate_update_request(self, mock_validate_update_data, mock_validate_bookmark_id):
        """Prueba la validación completa de solicitud de actualización"""
        # Configurar mocks
        mock_bookmark = mock.MagicMock()
        filtered_data = {"title": "Nuevo título"}
        
        # Caso exitoso
        mock_validate_bookmark_id.return_value = (True, mock_bookmark, None)
        mock_validate_update_data.return_value = (True, filtered_data, None)
        
        success, result, status_code = BookmarkValidationService.validate_update_request("123", {})
        self.assertTrue(success)
        self.assertEqual(result, {"bookmark": mock_bookmark, "data": filtered_data})
        self.assertEqual(status_code, status.HTTP_200_OK)
        
        # Caso error - bookmark no encontrado
        mock_validate_bookmark_id.return_value = (False, None, "Bookmark not found")
        
        success, result, status_code = BookmarkValidationService.validate_update_request("999", {})
        self.assertFalse(success)
        self.assertEqual(result, {"error": "Bookmark not found"})
        self.assertEqual(status_code, status.HTTP_404_NOT_FOUND)
        
        # Caso error - datos inválidos
        mock_validate_bookmark_id.return_value = (True, mock_bookmark, None)
        mock_validate_update_data.return_value = (False, None, "Datos inválidos")
        
        success, result, status_code = BookmarkValidationService.validate_update_request("123", {})
        self.assertFalse(success)
        self.assertEqual(result, {"error": "Datos inválidos"})
        self.assertEqual(status_code, status.HTTP_400_BAD_REQUEST)
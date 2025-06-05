import unittest
from unittest import mock

class TestBookmarkServices(unittest.TestCase):
    
    def test_services_imports(self):
        """Prueba que todos los servicios se pueden importar correctamente desde el módulo services"""
        try:
            from bookmark.services import (
                BookmarkValidationService,
                BookmarkRetrievalService,
                BookmarkProcessingService,
                BookmarkUpdatingService
            )
        except ImportError as e:
            self.fail(f"Fallo al importar los servicios: {e}")
    
    @mock.patch('bookmark.services.BookmarkValidationService')
    @mock.patch('bookmark.services.BookmarkRetrievalService')
    @mock.patch('bookmark.services.BookmarkProcessingService')
    @mock.patch('bookmark.services.BookmarkUpdatingService')
    def test_services_exposure(self, mock_updating, mock_processing, 
                             mock_retrieval, mock_validation):
        """Prueba que el módulo services expone correctamente todas las clases de servicio"""
        import bookmark.services as services
        
        self.assertIs(services.BookmarkValidationService, mock_validation)
        self.assertIs(services.BookmarkRetrievalService, mock_retrieval)
        self.assertIs(services.BookmarkProcessingService, mock_processing)
        self.assertIs(services.BookmarkUpdatingService, mock_updating)

if __name__ == '__main__':
    unittest.main()
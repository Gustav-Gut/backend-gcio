from unittest import TestCase, mock
import uuid
from datetime import datetime
from bookmark.services.processing import BookmarkProcessingService

class TestBookmarkProcessingService(TestCase):
    
    def test_process_bookmarks_with_actions_none(self):
        """Prueba el procesamiento cuando bookmarks es None"""
        result = BookmarkProcessingService.process_bookmarks_with_actions(None)
        self.assertEqual(result, [])
    
    def test_process_bookmarks_with_actions_empty(self):
        """Prueba el procesamiento cuando bookmarks está vacío"""
        result = BookmarkProcessingService.process_bookmarks_with_actions([])
        self.assertEqual(result, [])
    
    def test_process_bookmarks_without_actions(self):
        """Prueba el procesamiento de bookmarks sin acciones asociadas"""
        # Crear mock de bookmark sin acción
        bookmark = mock.MagicMock()
        bookmark.id = uuid.uuid4()
        bookmark.title = "Test Bookmark"
        bookmark.url = "https://test.com"
        bookmark.client_id = "client123"
        bookmark.status = True
        bookmark.created_at = datetime.now()
        bookmark.updated_at = datetime.now()
        bookmark.action = None
        
        result = BookmarkProcessingService.process_bookmarks_with_actions([bookmark])
        
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["title"], "Test Bookmark")
        self.assertEqual(result[0]["url"], "https://test.com")
        self.assertEqual(result[0]["client_id"], "client123")
        self.assertEqual(result[0]["status"], True)
        self.assertIsNone(result[0]["action"])
    
    def test_process_bookmarks_with_actions(self):
        """Prueba el procesamiento de bookmarks con acciones asociadas"""
        # Crear mock de acción
        action = mock.MagicMock()
        action.id = uuid.uuid4()
        action.category = "category1"
        action.result = "result1"
        action.icon = "icon1"
        action.color = "#FF0000"
        action.status = True
        
        # Crear mock de bookmark con acción
        bookmark = mock.MagicMock()
        bookmark.id = uuid.uuid4()
        bookmark.title = "Test Bookmark"
        bookmark.url = "https://test.com"
        bookmark.client_id = "client123"
        bookmark.status = True
        bookmark.created_at = datetime.now()
        bookmark.updated_at = datetime.now()
        bookmark.action = action
        
        result = BookmarkProcessingService.process_bookmarks_with_actions([bookmark])
        
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["title"], "Test Bookmark")
        self.assertEqual(result[0]["action"]["category"], "category1")
        self.assertEqual(result[0]["action"]["result"], "result1")
        self.assertEqual(result[0]["action"]["icon"], "icon1")
        self.assertEqual(result[0]["action"]["color"], "#FF0000")
        self.assertEqual(result[0]["action"]["status"], True)
        self.assertEqual(result[0]["action"]["id"], str(action.id))
    
    def test_process_multiple_bookmarks(self):
        """Prueba el procesamiento de múltiples bookmarks con y sin acciones"""
        # Crear mock de acción
        action = mock.MagicMock()
        action.id = uuid.uuid4()
        action.category = "category1"
        action.result = "result1"
        action.icon = "icon1"
        action.color = "#FF0000"
        action.status = True
        
        # Crear bookmark con acción
        bookmark1 = mock.MagicMock()
        bookmark1.id = uuid.uuid4()
        bookmark1.title = "Bookmark 1"
        bookmark1.url = "https://test1.com"
        bookmark1.client_id = "client123"
        bookmark1.status = True
        bookmark1.created_at = datetime.now()
        bookmark1.updated_at = datetime.now()
        bookmark1.action = action
        
        # Crear bookmark sin acción
        bookmark2 = mock.MagicMock()
        bookmark2.id = uuid.uuid4()
        bookmark2.title = "Bookmark 2"
        bookmark2.url = "https://test2.com"
        bookmark2.client_id = "client456"
        bookmark2.status = False
        bookmark2.created_at = datetime.now()
        bookmark2.updated_at = datetime.now()
        bookmark2.action = None
        
        result = BookmarkProcessingService.process_bookmarks_with_actions([bookmark1, bookmark2])
        
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0]["title"], "Bookmark 1")
        self.assertIsNotNone(result[0]["action"])
        self.assertEqual(result[1]["title"], "Bookmark 2")
        self.assertIsNone(result[1]["action"])
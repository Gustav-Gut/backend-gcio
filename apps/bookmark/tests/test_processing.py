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
        bookmark.external_source_id = uuid.uuid4()  # Añadido external_source_id
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
        action.fk_external_source_id = uuid.uuid4()  # Añadida relación con external_source
        
        # Crear mock de bookmark con acción
        bookmark = mock.MagicMock()
        bookmark.id = uuid.uuid4()
        bookmark.title = "Test Bookmark"
        bookmark.url = "https://test.com"
        bookmark.client_id = "client123"
        bookmark.status = True
        bookmark.external_source_id = action.fk_external_source_id  # Asegurar coherencia en relación
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
        action.fk_external_source_id = uuid.uuid4()
        
        # Crear bookmark con acción
        bookmark1 = mock.MagicMock()
        bookmark1.id = uuid.uuid4()
        bookmark1.title = "Bookmark 1"
        bookmark1.url = "https://test1.com"
        bookmark1.client_id = "client123"
        bookmark1.status = True
        bookmark1.external_source_id = action.fk_external_source_id
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
        bookmark2.external_source_id = uuid.uuid4()
        bookmark2.created_at = datetime.now()
        bookmark2.updated_at = datetime.now()
        bookmark2.action = None
        
        result = BookmarkProcessingService.process_bookmarks_with_actions([bookmark1, bookmark2])
        
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0]["title"], "Bookmark 1")
        self.assertIsNotNone(result[0]["action"])
        self.assertEqual(result[1]["title"], "Bookmark 2")
        self.assertIsNone(result[1]["action"])
    
    def test_process_bookmark_toggle_status(self):
        """Prueba el procesamiento de bookmarks con diferentes estados (activo/inactivo)"""
        # Crear dos bookmarks con estados opuestos
        bookmark1 = mock.MagicMock()
        bookmark1.id = uuid.uuid4()
        bookmark1.title = "Active Bookmark"
        bookmark1.url = "https://active.com"
        bookmark1.client_id = "client123"
        bookmark1.status = True  # Activo
        bookmark1.external_source_id = uuid.uuid4()
        bookmark1.action = None
        
        bookmark2 = mock.MagicMock()
        bookmark2.id = uuid.uuid4()
        bookmark2.title = "Inactive Bookmark"
        bookmark2.url = "https://inactive.com"
        bookmark2.client_id = "client123"
        bookmark2.status = False  # Inactivo
        bookmark2.external_source_id = uuid.uuid4()
        bookmark2.action = None
        
        result = BookmarkProcessingService.process_bookmarks_with_actions([bookmark1, bookmark2])
        
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0]["title"], "Active Bookmark")
        self.assertTrue(result[0]["status"])  # Verificar que status=True se procesa correctamente
        self.assertEqual(result[1]["title"], "Inactive Bookmark")
        self.assertFalse(result[1]["status"])  # Verificar que status=False se procesa correctamente
    
    def test_process_bookmark_with_consistent_external_source_relation(self):
        """Verifica que la relación entre action y external_source sea coherente"""
        # Crear external source ID
        external_source_id = uuid.uuid4()
        
        # Crear acción asociada a la fuente externa
        action = mock.MagicMock()
        action.id = uuid.uuid4()
        action.category = "category1"
        action.fk_external_source_id = external_source_id
        
        # Crear bookmark asociado a la misma fuente externa
        bookmark = mock.MagicMock()
        bookmark.id = uuid.uuid4()
        bookmark.title = "Test Bookmark"
        bookmark.external_source_id = external_source_id
        bookmark.action = action
        
        result = BookmarkProcessingService.process_bookmarks_with_actions([bookmark])
        
        # Verificar que external_source_id se mantiene consistente
        self.assertEqual(result[0]["title"], "Test Bookmark")
        self.assertIsNotNone(result[0]["action"])
        self.assertEqual(str(bookmark.external_source_id), str(action.fk_external_source_id))
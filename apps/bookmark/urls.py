from rest_framework.routers import DefaultRouter
from .views import BookmarkAPIView

router = DefaultRouter()
router.register(r'bookmark', BookmarkAPIView, basename='bookmark')
urlpatterns = router.urls
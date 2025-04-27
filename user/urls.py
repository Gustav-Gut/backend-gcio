from rest_framework.routers import DefaultRouter
from .views import UserAPIView

router = DefaultRouter()
router.register(r'user', UserAPIView, basename='user')
urlpatterns = router.urls
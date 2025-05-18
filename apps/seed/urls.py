from rest_framework.routers import DefaultRouter
from .views import SeedAPIView

router = DefaultRouter()
router.register(r'seed', SeedAPIView, basename='seed')
urlpatterns = router.urls
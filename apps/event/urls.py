from rest_framework.routers import DefaultRouter
from .views import EventViewSet

router = DefaultRouter()
router.register(r'event', EventViewSet, basename='event')

urlpatterns = router.urls 
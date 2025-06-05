from rest_framework.routers import DefaultRouter
from .views import FollowUpViewSet

router = DefaultRouter()
router.register(r'follow-up', FollowUpViewSet, basename='follow-up')
urlpatterns = router.urls

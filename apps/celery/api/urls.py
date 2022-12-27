from rest_framework.routers import DefaultRouter

from .views import CeleryTaskViewSet

router = DefaultRouter()
router.register('task', CeleryTaskViewSet, basename='celery-task')

urlpatterns = router.urls

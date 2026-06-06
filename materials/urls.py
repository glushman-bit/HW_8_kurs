from django.urls import path
from rest_framework.routers import SimpleRouter

from materials.apps import MaterialsConfig
from materials.views import CourseViewSet


app_name = MaterialsConfig.name

router = SimpleRouter()
router.register('courses', CourseViewSet)

urlpatterns = []
urlpatterns += router.urls
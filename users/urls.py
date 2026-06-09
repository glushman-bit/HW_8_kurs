from rest_framework.routers import SimpleRouter
from django.urls import path

from users.apps import UsersConfig
from users.views import UserViewSet, PaymentListAPIView

app_name = UsersConfig.name

router = SimpleRouter()
router.register('', UserViewSet)

urlpatterns = [
    path('payments/', PaymentListAPIView.as_view(), name='payments-list'),
]
urlpatterns += router.urls

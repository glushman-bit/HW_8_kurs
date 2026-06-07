from rest_framework import viewsets, generics
from rest_framework.filters import OrderingFilter, SearchFilter

from users.serializers import PaymentSerializer
from users.models import User, Payment
from users.serializers import UserSerializer
from django_filters.rest_framework import DjangoFilterBackend


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer


class PaymentListAPIView(generics.ListAPIView):
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer
    filter_backends = [DjangoFilterBackend, OrderingFilter, SearchFilter]
    search_fields = ('paid_course__name', 'paid_lesson__name',)
    filterset_fields = ('payment_method',)
    ordering_fields = ('date_payment',)

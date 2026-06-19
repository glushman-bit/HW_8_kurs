from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import generics, viewsets
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.permissions import AllowAny, IsAuthenticated

from users.models import Payment, User
from users.permissions import IsProfile
from users.serializers import PaymentSerializer, UserCreateSerializer, UserSerializer, UserViewSerializer
from users.services import create_stripe_price, create_stripe_product, create_stripe_session, get_status_session


class UserViewSet(viewsets.ModelViewSet):
    """Класс для работы с пользователями."""

    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (IsAuthenticated,)

    def get_permissions(self):
        """Получение прав доступа для изменения профиля пользователя."""

        if self.action in ["update", "partial_update"]:
            self.permission_classes = (IsProfile,)

        return super().get_permissions()

    def get_serializer_class(self):
        """Переопределение сериализатора. Добавлена защита от ошибки построения схемы Swagger."""

        if getattr(self, "swagger_fake_view", False):
            return UserSerializer

        if self.action == "retrieve":
            user = self.get_object()

            if user != self.request.user:
                return UserViewSerializer

        return UserSerializer


class UserCreateAPIView(generics.CreateAPIView):
    """Класс создания пользователя."""

    serializer_class = UserCreateSerializer
    permission_classes = (AllowAny,)


class PaymentListAPIView(generics.ListAPIView):
    """Класс вывода информации о платежах."""

    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer
    filter_backends = [DjangoFilterBackend, OrderingFilter, SearchFilter]
    search_fields = (
        'paid_course__name',
        'paid_lesson__name',
    )
    filterset_fields = ('payment_method',)
    ordering_fields = ('date_payment',)


class PaymentCreateAPIView(generics.CreateAPIView):
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer

    def perform_create(self, serializer):
        payment = serializer.save(user=self.request.user)

        if payment.paid_course:
            product_name = payment.paid_course.name
        else:
            product_name = payment.paid_lesson.name

        product = create_stripe_product(product_name)
        price = create_stripe_price(product.id, payment.amount)
        session_id, payment_link = create_stripe_session(price)
        payment.session_id = session_id
        payment.link = payment_link

        payment.save()


class PaymentRetrieveAPIView(generics.RetrieveAPIView):
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer

    def get_object(self):

        payment = super().get_object()
        get_status_session(payment)

        return payment

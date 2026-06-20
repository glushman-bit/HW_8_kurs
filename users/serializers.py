from rest_framework.serializers import ModelSerializer

from materials.serializers import CourseSerializer, LessonSerializer

from .models import Payment, User
from .validators import validate_payment_choice


class PaymentSerializer(ModelSerializer):
    """Сериализатор вывода платежей"""

    class Meta:
        model = Payment
        fields = "__all__"
        read_only_fields = (
            "user",
            "session_id",
            "link",
            "date_payment",
        )

    def validate(self, attrs):
        return validate_payment_choice(attrs)


class PaymentInfoSerializer(ModelSerializer):
    """Сериализатор вывода информации об оплаченных курсах и уроках."""

    paid_course = CourseSerializer()
    paid_lesson = LessonSerializer()

    class Meta:
        model = Payment
        fields = "__all__"


class UserSerializer(ModelSerializer):
    """Сериализатор вывода данных об истории платежей пользователей"""

    pay_history = PaymentInfoSerializer(source='payments', many=True, read_only=True)

    class Meta:
        model = User
        fields = ("id", "email", "phone", "avatar", "city", "pay_history")


class UserCreateSerializer(ModelSerializer):
    """Сериализатор создания пользователя"""

    class Meta:
        model = User
        fields = (
            "email",
            "password",
            "phone",
        )
        extra_kwargs = {"password": {"write_only": True}}

    def create(self, validated_data):
        user = User(email=validated_data["email"], is_active=True)
        user.set_password(validated_data["password"])
        user.save()

        return user


class UserViewSerializer(ModelSerializer):
    """Сериализатор представления данных о пользователях."""

    class Meta:
        model = User
        fields = (
            "id",
            "email",
            "avatar",
            "city",
        )

from rest_framework.serializers import ModelSerializer

from materials.serializers import CourseSerializer, LessonSerializer
from .models import User, Payment


class PaymentSerializer(ModelSerializer):
    """ Сериализатор вывода платежей """
    class Meta:
        model = Payment
        fields = "__all__"


class PaymentInfoSerializer(ModelSerializer):
    """ Сериализатор вывода платежей """
    paid_course = CourseSerializer()
    paid_lesson = LessonSerializer()

    class Meta:
        model = Payment
        fields = "__all__"


class UserSerializer(ModelSerializer):
    """ Сериализатор вывода пользователей """
    pay_history = PaymentInfoSerializer(source='payments',many=True, read_only=True)

    class Meta:
        model = User
        fields = ("id", "email", "phone", "avatar", "city", "pay_history")


class UserCreateSerializer(ModelSerializer):
    """ Сериализатор создания пользователя """
    class Meta:
        model = User
        fields = ("email", "password",)
        extra_kwargs = {
            "password": {"write_only": True}
        }


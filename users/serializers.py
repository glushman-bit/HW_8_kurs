from rest_framework.serializers import ModelSerializer

from .models import User, Payment


class UserSerializer(ModelSerializer):
    class Meta:
        model = User
        fields = ("id", "email", "phone", "avatar", "city",)


class PaymentSerializer(ModelSerializer):
    """ Сериализатор платежей """
    class Meta:
        model = Payment
        fields = "__all__"

from rest_framework.serializers import ValidationError


def validate_payment_choice(attrs):
    """Валидация полей оплаты курса и урока."""

    paid_course = attrs.get("paid_course")
    paid_lesson = attrs.get("paid_lesson")

    if not paid_course and not paid_lesson:
        raise ValidationError("Нужно указать оплачиваемый курс или урок.")

    if paid_course and paid_lesson:
        raise ValidationError("Можно оплатить либо курс, либо урок.")

    return attrs


def validate_payment_amount(value):
    """Проверка минимальной стоимости платежа."""

    if value < 10000:
        raise ValidationError("Цена не может быть менее 10000 копеек.")

    return value

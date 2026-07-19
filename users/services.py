import stripe
from rest_framework.serializers import ValidationError

from config import settings
from config.settings import STRIPE_API_KEY

if STRIPE_API_KEY:
    stripe.api_key = STRIPE_API_KEY


def create_stripe_product(name='Product'):
    """Создание продукта в Stripe."""

    product = stripe.Product.create(name=name)

    return product


def create_stripe_price(product_id, amount):
    """Создание продукта в Stripe."""

    if amount < 10000:
        raise ValidationError("Цена не может быть менее 10000 копеек.")

    price = stripe.Price.create(
        currency="rub",
        unit_amount=amount,
        product=product_id,
    )

    return price


def create_stripe_session(price):
    """Создание сессии в Stripe."""

    session = stripe.checkout.Session.create(
        success_url=settings.HOST_URL,
        line_items=[{"price": price.id, "quantity": 1}],
        mode="payment",
    )

    return session.id, session.url


def get_status_session(payment):
    """Получения статуса платежа Stripe."""

    if not payment.session_id:
        raise ValidationError("Для данного платежа отсутствует session_id.")

    session = stripe.checkout.Session.retrieve(payment.session_id)

    payment.status = session.payment_status
    payment.save(update_fields=["status"])

    return payment

import stripe

from config import settings
from config.settings import STRIPE_API_KEY


stripe.api_key = STRIPE_API_KEY

def create_stripe_product(name='Product'):
    """Создание продукта в Stripe."""

    product = stripe.Product.create(name=name)

    return product



def create_stripe_price(product_id, amount):
    """Создание продукта в Stripe."""

    price = stripe.Price.create(
      currency="rub",
      unit_amount=int(amount * 100),
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



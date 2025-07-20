import stripe
from django.conf import settings
from materials.models import Course

stripe.api_key = settings.STRIPE_API_KEY


def create_stripe_product(course: Course) -> str:
    product_data = {
        "name": course.name,
    }
    if course.description:
        product_data["description"] = course.description

    product = stripe.Product.create(**product_data)
    return product.id


def create_stripe_price(product_id: str, amount: int) -> str:
    price = stripe.Price.create(
        product=product_id,
        unit_amount=amount * 100,
        currency="rub",
    )
    return price.id


def create_stripe_session(price_id: str, success_url: str, cancel_url: str) -> dict:
    session = stripe.checkout.Session.create(
        payment_method_types=["card"],
        line_items=[
            {
                "price": price_id,
                "quantity": 1,
            }
        ],
        mode="payment",
        success_url=success_url,
        cancel_url=cancel_url,
    )
    return {"session_id": session.id, "payment_link": session.url}
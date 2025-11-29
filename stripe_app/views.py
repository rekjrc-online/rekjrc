from django.conf import settings
from django.http import HttpResponse
from django.shortcuts import redirect
from django.urls import reverse
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import TemplateView

import stripe
stripe.api_key = settings.STRIPE_SECRET_KEY

class PaymentSuccessView(TemplateView):
    template_name = "stripe_app/payment_success.html"

class PaymentCancelView(TemplateView):
    template_name = "stripe_app/payment_cancel.html"

PRODUCT_PRICE_MAP = {
    "clubmembership": {
        "price_id": "price_1SYYhPQalEiqoqnTC8IgJZNg",
        "type": "subscription"
    },
    "visitorentry": {
        "price_id": "price_1SYYiTQalEiqoqnTUJV9S6FJ",
        "type": "payment"
    },
    "memberentry": {
        "price_id": "price_1SYYnCQalEiqoqnTiOAKWysm",
        "type": "payment"
    },
    "memberguest": {
        "price_id": "price_1SYYnhQalEiqoqnTQGzXzqPp",
        "type": "payment"
    },
}

class CheckoutView(View):
    """Dynamically create a Stripe Checkout session based on product slug."""
    def post(self, request, product_slug, *args, **kwargs):
        priceobj = PRODUCT_PRICE_MAP.get(product_slug)
        print("priceobj:",priceobj)
        print("price_id",priceobj["price_id"])
        if not priceobj["price_id"]:
            return HttpResponse("Invalid product", status=400)
        session = stripe.checkout.Session.create(
            mode=priceobj["type"],
            line_items=[{"price": priceobj["price_id"], "quantity": 1}],
            success_url=request.build_absolute_uri(reverse("stripe:success")),
            cancel_url=request.build_absolute_uri(reverse("stripe:cancel")),
            metadata={"user_id": request.user.id},
        )
        return redirect(session.url, code=303)

@method_decorator(csrf_exempt, name="dispatch")
class StripeWebhookView(View):
    """Stripe webhook handler."""
    def post(self, request, *args, **kwargs):
        payload = request.body
        sig_header = request.META.get("HTTP_STRIPE_SIGNATURE")
        webhook_secret = settings.STRIPE_WEBHOOK_SECRET
        try:
            event = stripe.Webhook.construct_event(
                payload, sig_header, webhook_secret
            )
        except Exception:
            return HttpResponse(status=400)

        # Handle successful payments
        if event["type"] == "checkout.session.completed":
            session = event["data"]["object"]

            # Example: get metadata you attach later
            # user_id = session["metadata"].get("user_id")

            # TODO: Mark user or profile as upgraded
            print("Payment OK:", session["id"])

        return HttpResponse(status=200)

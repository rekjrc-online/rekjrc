# models.py
from django.db import models
from django.conf import settings

class StripePaymentLog(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    product_slug = models.CharField(max_length=100)
    stripe_session_id = models.CharField(max_length=255)
    stripe_payment_intent = models.CharField(max_length=255, blank=True, null=True)
    amount_total = models.IntegerField(blank=True, null=True)  # in cents
    currency = models.CharField(max_length=10, default="usd")
    status = models.CharField(max_length=50, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user} - {self.product_slug} - {self.status}"

"""
Send a confirmation email to the customer when an order is created.

Notes:
- We hook into post_save with created=True so updates don't re-trigger.
- The mail send is deferred via transaction.on_commit so the OrderItems
  (created in the same checkout transaction) are visible when the message
  is rendered, and a rolled-back checkout never sends an email.
- We never let an email failure (SMTP down, missing template, etc.) break
  the checkout — exceptions are logged and swallowed.
"""
import logging

from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.db import transaction
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.template.loader import render_to_string

from cover_house.orders.models import Order

logger = logging.getLogger(__name__)


def _send_order_created_email(order_id) -> None:
    try:
        order = (
            Order.objects
            .select_related("user")
            .prefetch_related("items")
            .get(pk=order_id)
        )
    except Order.DoesNotExist:
        return

    recipient = (order.user.email or "").strip()
    if not recipient:
        logger.info(
            "Order %s placed by user %s has no email — skipping confirmation.",
            order.order_number, order.user_id,
        )
        return

    context = {"order": order, "items": list(order.items.all())}
    subject = f"Order confirmation — {order.order_number}"
    text_body = render_to_string("orders/email/order_created.txt", context)

    from_email = (
        getattr(settings, "DEFAULT_FROM_EMAIL", None)
        or getattr(settings, "EMAIL_HOST_USER", None)
        or "no-reply@coverhouse.local"
    )

    message = EmailMultiAlternatives(
        subject=subject,
        body=text_body,
        from_email=from_email,
        to=[recipient],
    )
    try:
        html_body = render_to_string("orders/email/order_created.html", context)
        message.attach_alternative(html_body, "text/html")
    except Exception:
        # HTML template is optional — fall back to plain text.
        pass

    try:
        message.send(fail_silently=False)
    except Exception:
        logger.exception(
            "Failed to send order confirmation email for %s",
            order.order_number,
        )


@receiver(post_save, sender=Order)
def order_created(sender, instance, created, **kwargs):
    if not created:
        return
    # Defer until after the checkout transaction commits so OrderItems are
    # visible and a rolled-back checkout doesn't send a stray email.
    transaction.on_commit(lambda: _send_order_created_email(instance.pk))

from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class OrdersConfig(AppConfig):
    name = "cover_house.orders"
    verbose_name = _("Orders")

    def ready(self):
        # Register signal handlers (order confirmation email, etc.).
        from cover_house.orders import signals  # noqa: F401

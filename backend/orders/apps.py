from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class OrdersConfig(AppConfig):
    name = "backend.orders"
    verbose_name = _("Orders")
    default_auto_field = "django.db.models.BigAutoField"

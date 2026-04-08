from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class ExpensesConfig(AppConfig):
    name = "backend.expenses"
    verbose_name = _("Expenses")
    default_auto_field = "django.db.models.BigAutoField"

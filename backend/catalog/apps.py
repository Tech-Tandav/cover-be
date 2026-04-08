from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class CatalogConfig(AppConfig):
    name = "backend.catalog"
    verbose_name = _("Catalog")
    default_auto_field = "django.db.models.BigAutoField"

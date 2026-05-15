from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class PhonesConfig(AppConfig):
    name = "cover_house.phones"
    verbose_name = _("Phones")

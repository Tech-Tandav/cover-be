from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class CasesConfig(AppConfig):
    name = "cover_house.cases"
    verbose_name = _("Cases")

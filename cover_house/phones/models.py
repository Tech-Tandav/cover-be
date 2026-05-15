from django.db import models
from django.utils.translation import gettext_lazy as _

from cover_house.core.models import BaseModelWithSlug


class Brand(BaseModelWithSlug):
    """
    Mobile phone brand.
    """
    name = models.CharField(_("Brand name"), max_length=50, unique=True)
    logo = models.ImageField(upload_to="brands/logos/", blank=True, null=True)
    sort_order = models.PositiveSmallIntegerField(default=0)

    class Meta:
        ordering = ["sort_order", "name"]
        verbose_name = _("Brand")
        verbose_name_plural = _("Brands")

    def __str__(self):
        return self.name


class Series(BaseModelWithSlug):
    """
    Product line within a brand (e.g., 'Galaxy S Series', 'iPhone', 'Reno Series').
    """
    brand = models.ForeignKey(
        Brand, on_delete=models.CASCADE, related_name="series_set"
    )
    name = models.CharField(_("Series name"), max_length=100)
    sort_order = models.PositiveSmallIntegerField(default=0)

    class Meta:
        ordering = ["brand", "sort_order", "name"]
        verbose_name = _("Series")
        verbose_name_plural = _("Series")
        constraints = [
            models.UniqueConstraint(
                fields=["brand", "name"], name="unique_series_per_brand"
            ),
        ]

    def __str__(self):
        return f"{self.brand.name} — {self.name}"


class PhoneModel(BaseModelWithSlug):
    """
    Generation within a series (e.g., 'S10', 'iPhone 16', 'Reno 12').
    Variants like 'S10+' and 'S10e' hang off this row.
    """
    series = models.ForeignKey(
        Series, on_delete=models.CASCADE, related_name="phone_models"
    )
    name = models.CharField(_("Model name"), max_length=100)
    release_year = models.PositiveSmallIntegerField(blank=True, null=True)
    sort_order = models.PositiveSmallIntegerField(default=0)

    class Meta:
        ordering = ["series", "sort_order", "name"]
        verbose_name = _("Phone Model")
        verbose_name_plural = _("Phone Models")
        constraints = [
            models.UniqueConstraint(
                fields=["series", "name"], name="unique_model_per_series"
            ),
        ]

    def __str__(self):
        return f"{self.series.brand.name} {self.name}"


class PhoneVariant(BaseModelWithSlug):
    """
    Sellable phone SKU (e.g., 'S10', 'S10+', 'S10e'). This is the fitment key
    that cases are mapped to.
    """
    phone_model = models.ForeignKey(
        PhoneModel, on_delete=models.CASCADE, related_name="variants"
    )
    name = models.CharField(_("Variant name"), max_length=100)
    release_year = models.PositiveSmallIntegerField(blank=True, null=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["phone_model", "name"]
        verbose_name = _("Phone Variant")
        verbose_name_plural = _("Phone Variants")
        constraints = [
            models.UniqueConstraint(
                fields=["phone_model", "name"],
                name="unique_variant_per_model",
            ),
        ]

    def __str__(self):
        return f"{self.phone_model.series.brand.name} {self.name}"

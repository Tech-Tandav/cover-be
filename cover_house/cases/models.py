from django.db import models
from django.utils.translation import gettext_lazy as _

from cover_house.core.models import BaseModel, BaseModelWithSlug
from cover_house.phones.models import PhoneVariant


class CaseCategory(BaseModelWithSlug):
    """
    Type of case (Silicone, Clear, Wallet, Rugged, Flip, MagSafe, etc.).
    """
    name = models.CharField(_("Category name"), max_length=50, unique=True)
    sort_order = models.PositiveSmallIntegerField(default=0)

    class Meta:
        ordering = ["sort_order", "name"]
        verbose_name = _("Case Category")
        verbose_name_plural = _("Case Categories")

    def __str__(self):
        return self.name


class CaseColor(BaseModelWithSlug):
    """
    Global colour palette used by SKUs. A global table makes 'filter cases by
    colour' a clean join instead of a string match.
    """
    name = models.CharField(_("Colour name"), max_length=50, unique=True)
    hex_code = models.CharField(_("Hex code"), max_length=7, blank=True)
    sort_order = models.PositiveSmallIntegerField(default=0)

    class Meta:
        ordering = ["sort_order", "name"]
        verbose_name = _("Case Colour")
        verbose_name_plural = _("Case Colours")

    def __str__(self):
        return self.name


class CoverSku(BaseModelWithSlug):
    """
    Sellable cover product. One row per (design, phone variant, colour) combo.
    Carts and order lines reference this; stock is tracked here.
    """
    title = models.CharField(_("Title"), max_length=200)
    category = models.ForeignKey(
        CaseCategory, on_delete=models.PROTECT, related_name="skus"
    )
    phone_variant = models.ForeignKey(
        PhoneVariant, on_delete=models.PROTECT, related_name="skus"
    )
    color = models.ForeignKey(
        CaseColor,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="skus",
    )
    description = models.TextField(blank=True)
    sku_code = models.CharField(_("SKU code"), max_length=50, unique=True)
    base_price = models.DecimalField(
        _("Base price (NPR)"), max_digits=10, decimal_places=2
    )
    discount_price = models.DecimalField(
        _("Discount price (NPR)"),
        max_digits=10,
        decimal_places=2,
        blank=True,
        null=True,
        help_text=_("Optional sale price; if set, overrides base_price for display."),
    )
    stock_qty = models.PositiveIntegerField(default=0)
    fitment_notes = models.CharField(max_length=255, blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = _("Cover SKU")
        verbose_name_plural = _("Cover SKUs")
        constraints = [
            models.UniqueConstraint(
                fields=["title", "phone_variant", "color"],
                name="unique_cover_variant_color",
            ),
        ]
        indexes = [
            models.Index(fields=["phone_variant"]),
            models.Index(fields=["sku_code"]),
        ]

    def __str__(self):
        bits = [self.title, str(self.phone_variant)]
        if self.color_id:
            bits.append(self.color.name)
        return " • ".join(bits)

    @property
    def in_stock(self):
        return self.is_active and self.stock_qty > 0

    @property
    def effective_price(self):
        return self.discount_price if self.discount_price is not None else self.base_price


class CoverImage(BaseModel):
    """
    Gallery image attached to a CoverSku. One SKU has many images; the one
    flagged `is_primary` is used as the thumbnail in listings.
    """
    cover_sku = models.ForeignKey(
        CoverSku, on_delete=models.CASCADE, related_name="images"
    )
    image = models.ImageField(upload_to="covers/gallery/")
    alt_text = models.CharField(max_length=200, blank=True)
    is_primary = models.BooleanField(default=False)
    sort_order = models.PositiveSmallIntegerField(default=0)

    class Meta:
        ordering = ["sort_order", "created_at"]
        verbose_name = _("Cover Image")
        verbose_name_plural = _("Cover Images")
        indexes = [
            models.Index(fields=["cover_sku", "is_primary"]),
        ]

    def __str__(self):
        return f"Image for {self.cover_sku.title}"

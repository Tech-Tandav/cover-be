from django.db import models
from django.utils.translation import gettext_lazy as _

from cover_house.core.models import BaseModel, BaseModelWithSlug
from cover_house.phones.models import PhoneVariant


class SiteSettings(BaseModel):
    """
    Singleton row holding global storefront branding. Use
    `SiteSettings.load()` to fetch (creates the row on first call).
    """
    site_name = models.CharField(
        max_length=100, default="CoverHouse by E-Store"
    )
    tagline = models.CharField(max_length=160, blank=True, default="")
    logo = models.ImageField(upload_to="site/", blank=True, null=True)

    class Meta:
        verbose_name = _("Site settings")
        verbose_name_plural = _("Site settings")

    def __str__(self):
        return self.site_name

    @classmethod
    def load(cls):
        obj = cls.objects.first()
        if obj is None:
            obj = cls.objects.create()
        return obj

    def save(self, *args, **kwargs):
        # Enforce singleton: prevent creating a second row.
        if not self.pk and SiteSettings.objects.exists():
            raise ValueError("SiteSettings is a singleton; one row already exists.")
        super().save(*args, **kwargs)


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
    Sellable cover for a single phone variant. The cover may carry multiple
    case categories (silicone, clear…) and colours; the customer picks one of
    each at add-to-cart time. Stock is shared across all such combos.
    """
    phone_variant = models.OneToOneField(
        PhoneVariant, on_delete=models.PROTECT, related_name="cover"
    )
    categories = models.ManyToManyField(
        CaseCategory,
        blank=True,
        related_name="skus",
    )
    colors = models.ManyToManyField(
        CaseColor,
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
        indexes = [
            models.Index(fields=["sku_code"]),
        ]

    def __str__(self):
        return f"Cover for {self.phone_variant}"

    @property
    def display_name(self):
        """Customer-facing name. We display the phone variant string."""
        return str(self.phone_variant)

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
        return f"Image for {self.cover_sku.display_name}"

import secrets
from decimal import Decimal

from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _

from cover_house.cases.models import CoverSku
from cover_house.core.models import BaseModel


def _generate_order_number() -> str:
    """Short, URL-safe, mostly-unique order reference."""
    return f"ORD-{secrets.token_hex(5).upper()}"


# ─────────────────────────────────────────────────────────────────────────────
# Address
# ─────────────────────────────────────────────────────────────────────────────

class Address(BaseModel):
    """
    Customer shipping address. Nepal-specific fields (province, district).
    """

    class Province(models.TextChoices):
        KOSHI = "koshi", _("Koshi")
        MADHESH = "madhesh", _("Madhesh")
        BAGMATI = "bagmati", _("Bagmati")
        GANDAKI = "gandaki", _("Gandaki")
        LUMBINI = "lumbini", _("Lumbini")
        KARNALI = "karnali", _("Karnali")
        SUDURPASHCHIM = "sudurpashchim", _("Sudurpashchim")

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="addresses",
    )
    full_name = models.CharField(max_length=120)
    phone = models.CharField(max_length=20)
    province = models.CharField(
        max_length=20, choices=Province.choices, blank=True
    )
    district = models.CharField(max_length=80)
    city = models.CharField(max_length=80)
    street_address = models.CharField(max_length=255)
    landmark = models.CharField(max_length=120, blank=True)
    is_default = models.BooleanField(default=False)

    class Meta:
        ordering = ["-is_default", "-created_at"]
        verbose_name = _("Address")
        verbose_name_plural = _("Addresses")

    def __str__(self):
        return f"{self.full_name} — {self.city}, {self.district}"


# ─────────────────────────────────────────────────────────────────────────────
# Cart
# ─────────────────────────────────────────────────────────────────────────────

class Cart(BaseModel):
    """
    Shopping cart. Belongs to a user OR an anonymous session (one of the two
    must be set). Carts persist until checkout or expiry.
    """
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="carts",
    )
    session_key = models.CharField(max_length=64, blank=True, db_index=True)

    class Meta:
        verbose_name = _("Cart")
        verbose_name_plural = _("Carts")
        constraints = [
            models.CheckConstraint(
                check=models.Q(user__isnull=False) | ~models.Q(session_key=""),
                name="cart_has_user_or_session",
            ),
        ]

    def __str__(self):
        owner = self.user.username if self.user_id else f"guest:{self.session_key[:8]}"
        return f"Cart {self.id} ({owner})"

    @property
    def subtotal(self) -> Decimal:
        return sum(
            (item.line_total for item in self.items.all()), Decimal("0.00")
        )


class CartItem(BaseModel):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name="items")
    cover_sku = models.ForeignKey(
        CoverSku, on_delete=models.CASCADE, related_name="cart_items"
    )
    category = models.ForeignKey(
        "cases.CaseCategory",
        on_delete=models.PROTECT,
        related_name="+",
        null=True,
        blank=True,
    )
    color = models.ForeignKey(
        "cases.CaseColor",
        on_delete=models.PROTECT,
        related_name="+",
        null=True,
        blank=True,
    )
    quantity = models.PositiveIntegerField(default=1)

    class Meta:
        verbose_name = _("Cart Item")
        verbose_name_plural = _("Cart Items")
        constraints = [
            models.UniqueConstraint(
                fields=["cart", "cover_sku", "category", "color"],
                name="unique_combo_per_cart",
            ),
        ]

    def __str__(self):
        return f"{self.quantity} × {self.cover_sku.sku_code}"

    @property
    def unit_price(self) -> Decimal:
        return self.cover_sku.effective_price

    @property
    def line_total(self) -> Decimal:
        return self.unit_price * self.quantity


# ─────────────────────────────────────────────────────────────────────────────
# Order
# ─────────────────────────────────────────────────────────────────────────────

class Order(BaseModel):
    class Status(models.TextChoices):
        PENDING = "pending", _("Pending")
        CONFIRMED = "confirmed", _("Confirmed")
        PROCESSING = "processing", _("Processing")
        SHIPPED = "shipped", _("Shipped")
        DELIVERED = "delivered", _("Delivered")
        CANCELLED = "cancelled", _("Cancelled")
        RETURNED = "returned", _("Returned")

    class PaymentStatus(models.TextChoices):
        UNPAID = "unpaid", _("Unpaid")
        PAID = "paid", _("Paid")
        REFUNDED = "refunded", _("Refunded")
        FAILED = "failed", _("Failed")

    class PaymentMethod(models.TextChoices):
        COD = "cod", _("Cash on Delivery")
        ESEWA = "esewa", _("eSewa")
        KHALTI = "khalti", _("Khalti")
        FONEPAY = "fonepay", _("FonePay")
        IMEPAY = "imepay", _("IME Pay")
        BANK_TRANSFER = "bank_transfer", _("Bank Transfer")

    order_number = models.CharField(
        max_length=20, unique=True, default=_generate_order_number, editable=False
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="orders",
    )

    status = models.CharField(
        max_length=20, choices=Status.choices, default=Status.PENDING
    )
    payment_status = models.CharField(
        max_length=20, choices=PaymentStatus.choices, default=PaymentStatus.UNPAID
    )
    payment_method = models.CharField(
        max_length=20, choices=PaymentMethod.choices, default=PaymentMethod.COD
    )

    # Shipping address snapshot (so historical orders survive Address edits/deletes)
    ship_full_name = models.CharField(max_length=120)
    ship_phone = models.CharField(max_length=20)
    ship_province = models.CharField(max_length=20, blank=True)
    ship_district = models.CharField(max_length=80)
    ship_city = models.CharField(max_length=80)
    ship_street_address = models.CharField(max_length=255)
    ship_landmark = models.CharField(max_length=120, blank=True)

    # Money
    subtotal = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal("0.00"))
    shipping_fee = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal("0.00"))
    discount_total = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal("0.00"))
    grand_total = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal("0.00"))

    customer_note = models.TextField(blank=True)

    placed_at = models.DateTimeField(auto_now_add=True)
    paid_at = models.DateTimeField(null=True, blank=True)
    shipped_at = models.DateTimeField(null=True, blank=True)
    delivered_at = models.DateTimeField(null=True, blank=True)
    cancelled_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-placed_at"]
        verbose_name = _("Order")
        verbose_name_plural = _("Orders")
        indexes = [
            models.Index(fields=["user", "-placed_at"]),
            models.Index(fields=["status"]),
            models.Index(fields=["payment_status"]),
        ]

    def __str__(self):
        return self.order_number


class OrderItem(BaseModel):
    """
    Line item on an order. Stores snapshot fields so the line stays correct
    even if the underlying CoverSku is later edited or deleted.
    """
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")
    cover_sku = models.ForeignKey(
        CoverSku,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="order_items",
    )

    # Snapshot fields (populated at checkout time)
    sku_code = models.CharField(max_length=50)
    cover_title = models.CharField(max_length=200)
    phone_variant_name = models.CharField(max_length=120)
    category_name = models.CharField(max_length=50, blank=True)
    color_name = models.CharField(max_length=50, blank=True)

    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.PositiveIntegerField(default=1)
    line_total = models.DecimalField(max_digits=12, decimal_places=2)

    class Meta:
        verbose_name = _("Order Item")
        verbose_name_plural = _("Order Items")

    def __str__(self):
        return f"{self.quantity} × {self.sku_code} ({self.order.order_number})"

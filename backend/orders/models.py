from django.conf import settings
from django.db import models, transaction
from django.utils import timezone

from backend.catalog.models import Product, ProductType


class Order(models.Model):
    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("processing", "Processing"),
        ("shipped", "Shipped"),
        ("delivered", "Delivered"),
        ("cancelled", "Cancelled"),
    ]
    PAYMENT_CHOICES = [
        ("cod", "Cash on Delivery"),
        ("esewa", "eSewa"),
        ("khalti", "Khalti"),
        ("bank", "Bank Transfer"),
    ]

    order_number = models.CharField(max_length=32, unique=True, blank=True)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name="orders",
        null=True,
        blank=True,
    )

    customer_name = models.CharField(max_length=200)
    customer_phone = models.CharField(max_length=32)
    customer_email = models.EmailField(blank=True, default="")

    shipping_address = models.CharField(max_length=300)
    shipping_city = models.CharField(max_length=120, default="Pokhara")

    subtotal = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    shipping = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")
    payment_method = models.CharField(max_length=20, choices=PAYMENT_CHOICES, default="cod")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["status"]),
            models.Index(fields=["created_at"]),
        ]

    def __str__(self) -> str:
        return self.order_number or f"Order #{self.pk}"

    @property
    def item_count(self) -> int:
        return sum(item.quantity for item in self.items.all())

    def recalc_totals(self) -> None:
        self.subtotal = sum((item.subtotal for item in self.items.all()), start=0)
        self.total = self.subtotal + self.shipping

    def save(self, *args, **kwargs):
        if not self.order_number:
            year = timezone.now().year
            with transaction.atomic():
                last = (
                    Order.objects.select_for_update()
                    .filter(order_number__startswith=f"ESA-{year}-")
                    .order_by("-id")
                    .first()
                )
                next_seq = 1
                if last and last.order_number:
                    try:
                        next_seq = int(last.order_number.split("-")[-1]) + 1
                    except (ValueError, IndexError):
                        next_seq = 1
                self.order_number = f"ESA-{year}-{next_seq:04d}"
        super().save(*args, **kwargs)


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey(Product, on_delete=models.PROTECT, related_name="+")
    product_type = models.ForeignKey(
        ProductType,
        on_delete=models.PROTECT,
        related_name="+",
        null=True,
        blank=True,
    )

    # Snapshot fields — keep order history accurate even if product changes.
    product_name = models.CharField(max_length=200)
    product_image = models.URLField(blank=True, default="")
    variant_color = models.CharField(max_length=80, blank=True, default="")
    variant_size = models.CharField(max_length=40, blank=True, default="")
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.PositiveIntegerField(default=1)

    @property
    def subtotal(self):
        return self.unit_price * self.quantity

    def __str__(self) -> str:
        return f"{self.product_name} × {self.quantity}"

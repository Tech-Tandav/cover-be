import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ("catalog", "0001_initial"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="Order",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("order_number", models.CharField(blank=True, max_length=32, unique=True)),
                ("customer_name", models.CharField(max_length=200)),
                ("customer_phone", models.CharField(max_length=32)),
                ("customer_email", models.EmailField(blank=True, default="", max_length=254)),
                ("shipping_address", models.CharField(max_length=300)),
                ("shipping_city", models.CharField(default="Pokhara", max_length=120)),
                ("subtotal", models.DecimalField(decimal_places=2, default=0, max_digits=12)),
                ("shipping", models.DecimalField(decimal_places=2, default=0, max_digits=10)),
                ("total", models.DecimalField(decimal_places=2, default=0, max_digits=12)),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("pending", "Pending"),
                            ("processing", "Processing"),
                            ("shipped", "Shipped"),
                            ("delivered", "Delivered"),
                            ("cancelled", "Cancelled"),
                        ],
                        default="pending",
                        max_length=20,
                    ),
                ),
                (
                    "payment_method",
                    models.CharField(
                        choices=[
                            ("cod", "Cash on Delivery"),
                            ("esewa", "eSewa"),
                            ("khalti", "Khalti"),
                            ("bank", "Bank Transfer"),
                        ],
                        default="cod",
                        max_length=20,
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "user",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="orders",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "ordering": ["-created_at"],
            },
        ),
        migrations.CreateModel(
            name="OrderItem",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("product_name", models.CharField(max_length=200)),
                ("product_image", models.URLField(blank=True, default="")),
                ("unit_price", models.DecimalField(decimal_places=2, max_digits=10)),
                ("quantity", models.PositiveIntegerField(default=1)),
                (
                    "order",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="items",
                        to="orders.order",
                    ),
                ),
                (
                    "product",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="+",
                        to="catalog.product",
                    ),
                ),
            ],
        ),
        migrations.AddIndex(
            model_name="order",
            index=models.Index(fields=["status"], name="orders_orde_status_6f1f4d_idx"),
        ),
        migrations.AddIndex(
            model_name="order",
            index=models.Index(
                fields=["created_at"], name="orders_orde_created_a32bb7_idx"
            ),
        ),
    ]

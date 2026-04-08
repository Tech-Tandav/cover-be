import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Category",
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
                ("name", models.CharField(max_length=120, unique=True)),
                ("slug", models.SlugField(blank=True, max_length=140, unique=True)),
                ("description", models.TextField(blank=True, default="")),
                (
                    "icon",
                    models.CharField(
                        blank=True,
                        default="",
                        help_text="Lucide icon name used by the frontend (e.g. 'Smartphone').",
                        max_length=60,
                    ),
                ),
                (
                    "image",
                    models.ImageField(
                        blank=True, null=True, upload_to="categories/"
                    ),
                ),
                ("is_featured", models.BooleanField(default=False)),
                ("sort_order", models.PositiveIntegerField(default=0)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
            ],
            options={
                "verbose_name_plural": "Categories",
                "ordering": ["sort_order", "name"],
            },
        ),
        migrations.CreateModel(
            name="Product",
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
                ("name", models.CharField(max_length=200)),
                ("slug", models.SlugField(blank=True, max_length=220, unique=True)),
                ("brand", models.CharField(max_length=100)),
                (
                    "type",
                    models.CharField(
                        choices=[
                            ("Slim", "Slim"),
                            ("Rugged", "Rugged"),
                            ("Wallet", "Wallet"),
                            ("Transparent", "Transparent"),
                            ("Tempered Glass", "Tempered Glass"),
                            ("Matte", "Matte"),
                            ("Wall Charger", "Wall Charger"),
                            ("Cable", "Cable"),
                            ("Earbuds", "Earbuds"),
                            ("Smart Watch", "Smart Watch"),
                            ("Power Bank", "Power Bank"),
                            ("Speaker", "Speaker"),
                            ("Other", "Other"),
                        ],
                        default="Other",
                        max_length=60,
                    ),
                ),
                ("material", models.CharField(blank=True, default="", max_length=80)),
                ("color", models.CharField(blank=True, default="", max_length=80)),
                (
                    "compatible_with",
                    models.JSONField(
                        blank=True,
                        default=list,
                        help_text="List of phone models, e.g. ['iPhone 15 Pro', 'iPhone 15']",
                    ),
                ),
                ("price", models.DecimalField(decimal_places=2, max_digits=10)),
                (
                    "discount_price",
                    models.DecimalField(
                        blank=True, decimal_places=2, max_digits=10, null=True
                    ),
                ),
                ("stock", models.PositiveIntegerField(default=0)),
                ("description", models.TextField(blank=True, default="")),
                (
                    "image",
                    models.ImageField(
                        blank=True, null=True, upload_to="products/"
                    ),
                ),
                (
                    "rating",
                    models.DecimalField(decimal_places=2, default=0, max_digits=3),
                ),
                ("review_count", models.PositiveIntegerField(default=0)),
                ("is_featured", models.BooleanField(default=False)),
                ("is_new", models.BooleanField(default=False)),
                ("is_active", models.BooleanField(default=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "category",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="products",
                        to="catalog.category",
                    ),
                ),
            ],
            options={
                "ordering": ["-created_at"],
            },
        ),
        migrations.CreateModel(
            name="ProductImage",
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
                ("image", models.ImageField(upload_to="products/gallery/")),
                ("alt", models.CharField(blank=True, default="", max_length=160)),
                ("sort_order", models.PositiveIntegerField(default=0)),
                (
                    "product",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="images",
                        to="catalog.product",
                    ),
                ),
            ],
            options={
                "ordering": ["sort_order"],
            },
        ),
        migrations.AddIndex(
            model_name="product",
            index=models.Index(
                fields=["category", "is_active"],
                name="catalog_pro_categor_06b6c4_idx",
            ),
        ),
        migrations.AddIndex(
            model_name="product",
            index=models.Index(
                fields=["is_featured"], name="catalog_pro_is_feat_8d3d3a_idx"
            ),
        ),
    ]

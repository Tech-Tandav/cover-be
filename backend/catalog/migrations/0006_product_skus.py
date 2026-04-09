import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("catalog", "0005_phone_models"),
    ]

    operations = [
        migrations.AlterField(
            model_name="product",
            name="color",
            field=models.CharField(
                blank=True,
                default="",
                help_text=(
                    "Legacy single-color field. New products should define one "
                    "or more ProductSku rows instead."
                ),
                max_length=80,
            ),
        ),
        migrations.CreateModel(
            name="ProductSku",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("color", models.CharField(max_length=80)),
                (
                    "size",
                    models.CharField(
                        blank=True,
                        default="",
                        help_text=(
                            "Empty for products that don't have a size axis "
                            "(e.g. cases that fit only one device variant)."
                        ),
                        max_length=40,
                    ),
                ),
                (
                    "sku_code",
                    models.CharField(blank=True, max_length=64, unique=True),
                ),
                ("stock", models.PositiveIntegerField(default=0)),
                (
                    "image",
                    models.ImageField(
                        blank=True, null=True, upload_to="products/skus/"
                    ),
                ),
                ("is_active", models.BooleanField(default=True)),
                ("sort_order", models.PositiveIntegerField(default=0)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                (
                    "product",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="skus",
                        to="catalog.product",
                    ),
                ),
            ],
            options={
                "ordering": ["product_id", "sort_order", "color", "size"],
            },
        ),
        migrations.AddConstraint(
            model_name="productsku",
            constraint=models.UniqueConstraint(
                fields=("product", "color", "size"),
                name="productsku_unique_color_size_per_product",
            ),
        ),
    ]

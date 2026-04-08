import django.db.models.deletion
from django.db import migrations, models


def link_brands_to_all_categories(apps, schema_editor):
    """Existing brands have no category links yet. To keep old products visible
    in the dashboard form (which now filters brands by selected category),
    associate every existing brand with every existing category. The owner can
    trim the relations from /admin/ afterwards."""
    Brand = apps.get_model("catalog", "Brand")
    Category = apps.get_model("catalog", "Category")
    category_ids = list(Category.objects.values_list("id", flat=True))
    if not category_ids:
        return
    for brand in Brand.objects.all():
        brand.categories.set(category_ids)


class Migration(migrations.Migration):

    dependencies = [
        ("catalog", "0003_dynamic_brands"),
    ]

    operations = [
        # 1. Brand <-> Category M2M.
        migrations.AddField(
            model_name="brand",
            name="categories",
            field=models.ManyToManyField(
                blank=True,
                help_text=(
                    "Categories this brand appears in. Used to filter the brand "
                    "dropdown in the product form once a category is selected."
                ),
                related_name="brands",
                to="catalog.category",
            ),
        ),
        migrations.RunPython(
            link_brands_to_all_categories,
            reverse_code=migrations.RunPython.noop,
        ),
        # 2. Variant model.
        migrations.CreateModel(
            name="Variant",
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
                ("name", models.CharField(max_length=120)),
                ("slug", models.SlugField(blank=True, max_length=160)),
                ("sort_order", models.PositiveIntegerField(default=0)),
                ("is_active", models.BooleanField(default=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                (
                    "brand",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="variants",
                        to="catalog.brand",
                    ),
                ),
            ],
            options={
                "ordering": ["brand__name", "sort_order", "name"],
            },
        ),
        migrations.AddConstraint(
            model_name="variant",
            constraint=models.UniqueConstraint(
                fields=("brand", "name"), name="variant_unique_per_brand"
            ),
        ),
        migrations.AddConstraint(
            model_name="variant",
            constraint=models.UniqueConstraint(
                fields=("brand", "slug"), name="variant_slug_unique_per_brand"
            ),
        ),
        # 3. Product.variants M2M.
        migrations.AddField(
            model_name="product",
            name="variants",
            field=models.ManyToManyField(
                blank=True,
                help_text="Device variants this product is compatible with.",
                related_name="products",
                to="catalog.variant",
            ),
        ),
        # 4. Drop the legacy fields and the ProductType model. Existing data
        # in `type` and `compatible_with` is intentionally not migrated; the
        # owner re-tags products with variants from the dashboard.
        migrations.RemoveField(
            model_name="product",
            name="type",
        ),
        migrations.RemoveField(
            model_name="product",
            name="compatible_with",
        ),
        migrations.DeleteModel(
            name="ProductType",
        ),
    ]

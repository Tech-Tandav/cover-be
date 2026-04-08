import django.db.models.deletion
from django.db import migrations, models
from django.utils.text import slugify


def populate_brands(apps, schema_editor):
    Product = apps.get_model("catalog", "Product")
    Brand = apps.get_model("catalog", "Brand")

    names = {
        (name or "").strip()
        for name in Product.objects.values_list("brand", flat=True).distinct()
    }
    names.discard("")
    names.add("Unbranded")  # fallback for any rows with empty brand

    name_to_obj = {}
    for idx, name in enumerate(sorted(names)):
        obj, _ = Brand.objects.get_or_create(
            name=name,
            defaults={"slug": slugify(name)[:120], "sort_order": idx},
        )
        name_to_obj[name] = obj

    fallback = name_to_obj["Unbranded"]
    for product in Product.objects.all():
        product.brand_new = name_to_obj.get((product.brand or "").strip(), fallback)
        product.save(update_fields=["brand_new"])


class Migration(migrations.Migration):

    dependencies = [
        ("catalog", "0002_dynamic_product_types"),
    ]

    operations = [
        migrations.CreateModel(
            name="Brand",
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
                ("name", models.CharField(max_length=100, unique=True)),
                ("slug", models.SlugField(blank=True, max_length=120, unique=True)),
                ("logo", models.ImageField(blank=True, null=True, upload_to="brands/")),
                ("sort_order", models.PositiveIntegerField(default=0)),
                ("is_active", models.BooleanField(default=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
            ],
            options={"ordering": ["sort_order", "name"]},
        ),
        migrations.AddField(
            model_name="product",
            name="brand_new",
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name="products",
                to="catalog.brand",
            ),
        ),
        migrations.RunPython(
            populate_brands,
            reverse_code=migrations.RunPython.noop,
        ),
        migrations.RemoveField(
            model_name="product",
            name="brand",
        ),
        migrations.RenameField(
            model_name="product",
            old_name="brand_new",
            new_name="brand",
        ),
        migrations.AlterField(
            model_name="product",
            name="brand",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.PROTECT,
                related_name="products",
                to="catalog.brand",
            ),
        ),
    ]

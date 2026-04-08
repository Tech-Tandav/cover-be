import django.db.models.deletion
from django.db import migrations, models
from django.utils.text import slugify


def populate_product_types(apps, schema_editor):
    Product = apps.get_model("catalog", "Product")
    ProductType = apps.get_model("catalog", "ProductType")

    names = {
        (name or "").strip()
        for name in Product.objects.values_list("type", flat=True).distinct()
    }
    names.discard("")
    names.add("Other")  # fallback for any rows with empty/missing type

    name_to_obj = {}
    for idx, name in enumerate(sorted(names)):
        obj, _ = ProductType.objects.get_or_create(
            name=name,
            defaults={"slug": slugify(name)[:80], "sort_order": idx},
        )
        name_to_obj[name] = obj

    other = name_to_obj["Other"]
    for product in Product.objects.all():
        product.type_new = name_to_obj.get((product.type or "").strip(), other)
        product.save(update_fields=["type_new"])


class Migration(migrations.Migration):

    dependencies = [
        ("catalog", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="ProductType",
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
                ("name", models.CharField(max_length=60, unique=True)),
                ("slug", models.SlugField(blank=True, max_length=80, unique=True)),
                ("sort_order", models.PositiveIntegerField(default=0)),
                ("is_active", models.BooleanField(default=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
            ],
            options={"ordering": ["sort_order", "name"]},
        ),
        migrations.AddField(
            model_name="product",
            name="type_new",
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name="products",
                to="catalog.producttype",
            ),
        ),
        migrations.RunPython(
            populate_product_types,
            reverse_code=migrations.RunPython.noop,
        ),
        migrations.RemoveField(
            model_name="product",
            name="type",
        ),
        migrations.RenameField(
            model_name="product",
            old_name="type_new",
            new_name="type",
        ),
        migrations.AlterField(
            model_name="product",
            name="type",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.PROTECT,
                related_name="products",
                to="catalog.producttype",
            ),
        ),
    ]

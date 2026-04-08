import django.db.models.deletion
from django.db import migrations, models


def create_default_models_and_relink(apps, schema_editor):
    """For every Brand that already has Variants attached, create one
    ``Default`` PhoneModel under that brand and point each variant at it.
    The owner can rename / split the default model into real ones from
    /admin/ afterwards."""
    Brand = apps.get_model("catalog", "Brand")
    PhoneModel = apps.get_model("catalog", "PhoneModel")
    Variant = apps.get_model("catalog", "Variant")

    brand_to_default: dict[int, "PhoneModel"] = {}
    for brand in Brand.objects.all():
        if not brand.variants.exists():
            continue
        pm, _ = PhoneModel.objects.get_or_create(
            brand=brand,
            name="Default",
            defaults={"slug": "default"},
        )
        brand_to_default[brand.id] = pm

    for variant in Variant.objects.all():
        pm = brand_to_default.get(variant.brand_id)
        if pm:
            variant.model_new = pm
            variant.save(update_fields=["model_new"])


class Migration(migrations.Migration):

    dependencies = [
        ("catalog", "0004_variants_categories"),
    ]

    operations = [
        # 1. PhoneModel.
        migrations.CreateModel(
            name="PhoneModel",
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
                        related_name="phone_models",
                        to="catalog.brand",
                    ),
                ),
            ],
            options={
                "ordering": ["brand__name", "sort_order", "name"],
            },
        ),
        migrations.AddConstraint(
            model_name="phonemodel",
            constraint=models.UniqueConstraint(
                fields=("brand", "name"), name="phonemodel_unique_per_brand"
            ),
        ),
        migrations.AddConstraint(
            model_name="phonemodel",
            constraint=models.UniqueConstraint(
                fields=("brand", "slug"), name="phonemodel_slug_unique_per_brand"
            ),
        ),

        # 2. Temp FK on Variant pointing at the new PhoneModel. Uses a
        # disposable related_name so it doesn't collide with anything.
        migrations.AddField(
            model_name="variant",
            name="model_new",
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="+",
                to="catalog.phonemodel",
            ),
        ),

        # 3. Backfill model_new for each existing variant.
        migrations.RunPython(
            create_default_models_and_relink,
            reverse_code=migrations.RunPython.noop,
        ),

        # 4. Drop the old (brand, ...) unique constraints before removing the
        # brand FK that they reference.
        migrations.RemoveConstraint(
            model_name="variant",
            name="variant_unique_per_brand",
        ),
        migrations.RemoveConstraint(
            model_name="variant",
            name="variant_slug_unique_per_brand",
        ),

        # 5. Drop the old brand FK on Variant.
        migrations.RemoveField(
            model_name="variant",
            name="brand",
        ),

        # 6. Rename model_new -> model.
        migrations.RenameField(
            model_name="variant",
            old_name="model_new",
            new_name="model",
        ),

        # 7. Make it non-null with the final related_name and ordering.
        migrations.AlterField(
            model_name="variant",
            name="model",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="variants",
                to="catalog.phonemodel",
            ),
        ),
        migrations.AlterModelOptions(
            name="variant",
            options={
                "ordering": [
                    "model__brand__name",
                    "model__name",
                    "sort_order",
                    "name",
                ]
            },
        ),

        # 8. New uniqueness scoped to model.
        migrations.AddConstraint(
            model_name="variant",
            constraint=models.UniqueConstraint(
                fields=("model", "name"), name="variant_unique_per_model"
            ),
        ),
        migrations.AddConstraint(
            model_name="variant",
            constraint=models.UniqueConstraint(
                fields=("model", "slug"), name="variant_slug_unique_per_model"
            ),
        ),
    ]

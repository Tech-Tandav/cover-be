from django.db import migrations, models


def backfill_full_name(apps, schema_editor):
    PhoneVariant = apps.get_model("phones", "PhoneVariant")
    for v in PhoneVariant.objects.select_related(
        "phone_model__series__brand"
    ).all():
        model = v.phone_model
        series = model.series
        brand = series.brand
        v.full_name = (
            f"{brand.name} > {series.name} > {model.name} > {v.name}"
        )
        PhoneVariant.objects.filter(pk=v.pk).update(full_name=v.full_name)


def noop(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ("phones", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="phonevariant",
            name="full_name",
            field=models.CharField(
                blank=True,
                default="",
                editable=False,
                max_length=500,
                verbose_name="Full name",
            ),
        ),
        migrations.RunPython(backfill_full_name, noop),
    ]

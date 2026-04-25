from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("site_settings", "0002_alter_sitesettings_map_embed_url_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="sitesettings",
            name="repair_model",
            field=models.CharField(blank=True, default="iPhone 15 Pro", max_length=120),
        ),
        migrations.AddField(
            model_name="sitesettings",
            name="repair_prices",
            field=models.JSONField(blank=True, default=list),
        ),
    ]

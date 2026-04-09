from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("site_settings", "0001_initial"),
    ]

    operations = [
        migrations.AlterField(
            model_name="sitesettings",
            name="map_embed_url",
            field=models.URLField(
                blank=True,
                default="https://www.openstreetmap.org/export/embed.html?bbox=83.96%2C28.20%2C84.00%2C28.23&layer=mapnik&marker=28.215%2C83.985",
                max_length=500,
            ),
        ),
        migrations.AlterField(
            model_name="sitesettings",
            name="map_directions_url",
            field=models.URLField(
                blank=True,
                default="https://www.google.com/maps/search/?api=1&query=Naya+Bazaar+Pokhara+Nepal",
                max_length=500,
            ),
        ),
    ]

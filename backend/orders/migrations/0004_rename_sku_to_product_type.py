from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("orders", "0003_rename_orders_orde_status_6f1f4d_idx_orders_orde_status_c6dd84_idx_and_more"),
        ("catalog", "0008_rename_productsku_to_producttype"),
    ]

    operations = [
        migrations.RenameField(
            model_name="orderitem",
            old_name="sku",
            new_name="product_type",
        ),
    ]

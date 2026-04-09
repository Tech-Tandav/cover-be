from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("catalog", "0007_store_and_more"),
        ("orders", "0003_rename_orders_orde_status_6f1f4d_idx_orders_orde_status_c6dd84_idx_and_more"),
    ]

    operations = [
        # 1. Rename the model ProductSku → ProductType
        migrations.RenameModel(
            old_name="ProductSku",
            new_name="ProductType",
        ),
        # 2. Rename the constraint
        migrations.RemoveConstraint(
            model_name="producttype",
            name="productsku_unique_color_size_per_product",
        ),
        migrations.AddConstraint(
            model_name="producttype",
            constraint=models.UniqueConstraint(
                fields=["product", "color", "size"],
                name="producttype_unique_color_size_per_product",
            ),
        ),
        # 3. Update image upload_to path
        migrations.AlterField(
            model_name="producttype",
            name="image",
            field=models.ImageField(blank=True, null=True, upload_to="products/types/"),
        ),
        # 4. Remove color, stock, image from Product
        migrations.RemoveField(
            model_name="product",
            name="color",
        ),
        migrations.RemoveField(
            model_name="product",
            name="stock",
        ),
        migrations.RemoveField(
            model_name="product",
            name="image",
        ),
    ]

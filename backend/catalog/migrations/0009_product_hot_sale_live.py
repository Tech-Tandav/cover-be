from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("catalog", "0008_rename_productsku_to_producttype"),
    ]

    operations = [
        # Rename is_featured → hot_sale_live
        migrations.RenameField(
            model_name="product",
            old_name="is_featured",
            new_name="hot_sale_live",
        ),
        # Update the index (drop old, add new)
        migrations.RemoveIndex(
            model_name="product",
            name="catalog_pro_is_feat_8d3d3a_idx",
        ),
        migrations.AddIndex(
            model_name="product",
            index=models.Index(
                fields=["hot_sale_live"],
                name="catalog_pro_hot_sal_idx",
            ),
        ),
    ]

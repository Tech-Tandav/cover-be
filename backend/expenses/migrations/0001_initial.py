import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="Expense",
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
                ("title", models.CharField(max_length=200)),
                ("amount", models.DecimalField(decimal_places=2, max_digits=12)),
                (
                    "category",
                    models.CharField(
                        choices=[
                            ("inventory", "Inventory"),
                            ("rent", "Rent"),
                            ("utilities", "Utilities"),
                            ("salary", "Salary"),
                            ("marketing", "Marketing"),
                            ("transport", "Transport"),
                            ("supplies", "Supplies"),
                            ("other", "Other"),
                        ],
                        default="other",
                        max_length=20,
                    ),
                ),
                (
                    "source",
                    models.CharField(
                        choices=[
                            ("online", "Online"),
                            ("offline", "Offline (cash)"),
                        ],
                        default="offline",
                        max_length=20,
                    ),
                ),
                ("note", models.TextField(blank=True, default="")),
                ("date", models.DateField()),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                (
                    "created_by",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="expenses",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "ordering": ["-date", "-created_at"],
            },
        ),
        migrations.AddIndex(
            model_name="expense",
            index=models.Index(fields=["date"], name="expenses_ex_date_8b1c19_idx"),
        ),
        migrations.AddIndex(
            model_name="expense",
            index=models.Index(fields=["category"], name="expenses_ex_categor_4cf78c_idx"),
        ),
        migrations.AddIndex(
            model_name="expense",
            index=models.Index(fields=["source"], name="expenses_ex_source_70a342_idx"),
        ),
    ]

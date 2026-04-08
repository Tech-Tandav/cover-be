from django.conf import settings
from django.db import models


class Expense(models.Model):
    CATEGORY_CHOICES = [
        ("inventory", "Inventory"),
        ("rent", "Rent"),
        ("utilities", "Utilities"),
        ("salary", "Salary"),
        ("marketing", "Marketing"),
        ("transport", "Transport"),
        ("supplies", "Supplies"),
        ("other", "Other"),
    ]
    SOURCE_CHOICES = [
        ("online", "Online"),
        ("offline", "Offline (cash)"),
    ]

    title = models.CharField(max_length=200)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default="other")
    source = models.CharField(max_length=20, choices=SOURCE_CHOICES, default="offline")
    note = models.TextField(blank=True, default="")
    date = models.DateField()

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="expenses",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-date", "-created_at"]
        indexes = [
            models.Index(fields=["date"]),
            models.Index(fields=["category"]),
            models.Index(fields=["source"]),
        ]

    def __str__(self) -> str:
        return f"{self.title} — Rs. {self.amount}"

from django.contrib import admin

from .models import Expense


@admin.register(Expense)
class ExpenseAdmin(admin.ModelAdmin):
    list_display = ("title", "amount", "category", "source", "date", "created_at")
    list_filter = ("category", "source", "date")
    search_fields = ("title", "note")
    date_hierarchy = "date"

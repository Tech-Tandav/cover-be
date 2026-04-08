from rest_framework import serializers

from backend.expenses.models import Expense


class ExpenseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Expense
        fields = [
            "id",
            "title",
            "amount",
            "category",
            "source",
            "note",
            "date",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]

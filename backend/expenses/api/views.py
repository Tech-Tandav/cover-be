from django.db.models import Sum
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response

from backend.expenses.models import Expense

from .serializers import ExpenseSerializer


class ExpenseViewSet(viewsets.ModelViewSet):
    queryset = Expense.objects.all()
    serializer_class = ExpenseSerializer
    permission_classes = [IsAdminUser]

    filter_backends = [DjangoFilterBackend, filters.OrderingFilter, filters.SearchFilter]
    filterset_fields = {
        "category": ["exact"],
        "source": ["exact"],
        "date": ["exact", "gte", "lte"],
    }
    search_fields = ["title", "note"]
    ordering_fields = ["date", "amount", "created_at"]
    ordering = ["-date", "-created_at"]

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

    @action(detail=False, methods=["get"])
    def summary(self, request):
        qs = self.filter_queryset(self.get_queryset())
        total = qs.aggregate(s=Sum("amount"))["s"] or 0
        online = qs.filter(source="online").aggregate(s=Sum("amount"))["s"] or 0
        offline = qs.filter(source="offline").aggregate(s=Sum("amount"))["s"] or 0
        by_category = (
            qs.values("category")
            .annotate(total=Sum("amount"))
            .order_by("-total")
        )
        return Response(
            {
                "total": total,
                "online": online,
                "offline": offline,
                "by_category": {row["category"]: row["total"] for row in by_category},
            }
        )

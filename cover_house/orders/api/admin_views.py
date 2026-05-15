"""
Admin order management. Mounted under /api/admin/.
"""
from django.utils import timezone
from rest_framework import serializers, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response

from cover_house.orders.models import Order

from .serializers import OrderSerializer


class OrderStatusUpdateSerializer(serializers.Serializer):
    status = serializers.ChoiceField(choices=Order.Status.choices, required=False)
    payment_status = serializers.ChoiceField(
        choices=Order.PaymentStatus.choices, required=False
    )


class OrderAdminViewSet(viewsets.ReadOnlyModelViewSet):
    """
    GET    /api/admin/orders/                    all orders
    GET    /api/admin/orders/{order_number}/
    PATCH  /api/admin/orders/{order_number}/update_status/
    """
    queryset = Order.objects.select_related("user").prefetch_related("items")
    serializer_class = OrderSerializer
    permission_classes = [IsAdminUser]
    lookup_field = "order_number"

    def get_queryset(self):
        qs = super().get_queryset()
        p = self.request.query_params
        if p.get("status"):
            qs = qs.filter(status=p["status"])
        if p.get("payment_status"):
            qs = qs.filter(payment_status=p["payment_status"])
        if p.get("user"):
            qs = qs.filter(user__username=p["user"])
        return qs

    @action(detail=True, methods=["patch"])
    def update_status(self, request, order_number=None):
        order = self.get_object()
        ser = OrderStatusUpdateSerializer(data=request.data)
        ser.is_valid(raise_exception=True)

        new_status = ser.validated_data.get("status")
        new_payment = ser.validated_data.get("payment_status")

        update_fields = ["updated_at"]
        now = timezone.now()

        if new_status and new_status != order.status:
            order.status = new_status
            update_fields.append("status")
            if new_status == Order.Status.SHIPPED and not order.shipped_at:
                order.shipped_at = now
                update_fields.append("shipped_at")
            elif new_status == Order.Status.DELIVERED and not order.delivered_at:
                order.delivered_at = now
                update_fields.append("delivered_at")
            elif new_status == Order.Status.CANCELLED and not order.cancelled_at:
                order.cancelled_at = now
                update_fields.append("cancelled_at")

        if new_payment and new_payment != order.payment_status:
            order.payment_status = new_payment
            update_fields.append("payment_status")
            if new_payment == Order.PaymentStatus.PAID and not order.paid_at:
                order.paid_at = now
                update_fields.append("paid_at")

        order.save(update_fields=update_fields)
        return Response(OrderSerializer(order).data)

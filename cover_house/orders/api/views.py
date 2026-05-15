from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework import mixins, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from cover_house.orders.models import Address, Cart, CartItem, Order

from .serializers import (
    AddressSerializer,
    CartItemSerializer,
    CartItemWriteSerializer,
    CartSerializer,
    CheckoutSerializer,
    OrderSerializer,
)


# ─── Address ─────────────────────────────────────────────────────────────────

class AddressViewSet(viewsets.ModelViewSet):
    """
    Full CRUD on the current user's addresses.
    GET    /api/addresses/
    POST   /api/addresses/
    PATCH  /api/addresses/{id}/
    DELETE /api/addresses/{id}/
    """
    serializer_class = AddressSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Address.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


# ─── Cart ────────────────────────────────────────────────────────────────────

def _get_or_create_cart(user) -> Cart:
    cart, _ = Cart.objects.get_or_create(user=user)
    return cart


class CartView(APIView):
    """
    GET    /api/cart/    current user's cart
    DELETE /api/cart/    empty the cart (does not delete the Cart row)
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        cart = _get_or_create_cart(request.user)
        return Response(CartSerializer(cart).data)

    def delete(self, request):
        cart = _get_or_create_cart(request.user)
        cart.items.all().delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class CartItemViewSet(
    mixins.CreateModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet,
):
    """
    POST   /api/cart/items/        add or increment a SKU in the cart
    PATCH  /api/cart/items/{id}/   update quantity
    DELETE /api/cart/items/{id}/   remove item
    """
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return CartItem.objects.filter(cart__user=self.request.user)

    def get_serializer_class(self):
        if self.action in {"create", "update", "partial_update"}:
            return CartItemWriteSerializer
        return CartItemSerializer

    def create(self, request, *args, **kwargs):
        cart = _get_or_create_cart(request.user)
        ser = CartItemWriteSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        sku = ser.validated_data["sku_obj"]
        qty = ser.validated_data["quantity"]

        item, created = CartItem.objects.get_or_create(
            cart=cart, cover_sku=sku, defaults={"quantity": qty}
        )
        if not created:
            new_qty = item.quantity + qty
            if new_qty > sku.stock_qty:
                return Response(
                    {"quantity": f"Only {sku.stock_qty} in stock."},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            item.quantity = new_qty
            item.save(update_fields=["quantity", "updated_at"])

        return Response(
            CartItemSerializer(item).data,
            status=status.HTTP_201_CREATED if created else status.HTTP_200_OK,
        )

    def partial_update(self, request, *args, **kwargs):
        item = self.get_object()
        qty = request.data.get("quantity")
        if qty is None:
            return Response(
                {"quantity": "Required."}, status=status.HTTP_400_BAD_REQUEST
            )
        try:
            qty = int(qty)
        except (TypeError, ValueError):
            return Response(
                {"quantity": "Must be an integer."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if qty < 1:
            return Response(
                {"quantity": "Must be >= 1."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if qty > item.cover_sku.stock_qty:
            return Response(
                {"quantity": f"Only {item.cover_sku.stock_qty} in stock."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        item.quantity = qty
        item.save(update_fields=["quantity", "updated_at"])
        return Response(CartItemSerializer(item).data)


# ─── Checkout ────────────────────────────────────────────────────────────────

class CheckoutView(APIView):
    """
    POST /api/checkout/
    Body: see CheckoutSerializer (address_id OR inline ship fields, payment_method).
    Returns: the created Order.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        ser = CheckoutSerializer(data=request.data, context={"request": request})
        ser.is_valid(raise_exception=True)
        order = ser.save()
        return Response(
            OrderSerializer(order).data, status=status.HTTP_201_CREATED
        )


# ─── Orders (customer-facing) ────────────────────────────────────────────────

class OrderViewSet(viewsets.ReadOnlyModelViewSet):
    """
    GET /api/orders/                       current user's orders
    GET /api/orders/{order_number}/        order detail
    POST /api/orders/{order_number}/cancel/  cancel a pending order
    """
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = "order_number"

    def get_queryset(self):
        return (
            Order.objects.filter(user=self.request.user)
            .prefetch_related("items")
        )

    @action(detail=True, methods=["post"])
    def cancel(self, request, order_number=None):
        order = self.get_object()
        if order.status not in {Order.Status.PENDING, Order.Status.CONFIRMED}:
            return Response(
                {"detail": f"Cannot cancel an order in '{order.status}' state."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        order.status = Order.Status.CANCELLED
        order.cancelled_at = timezone.now()
        order.save(update_fields=["status", "cancelled_at", "updated_at"])
        return Response(OrderSerializer(order).data)

from decimal import Decimal

from django.db import transaction
from rest_framework import serializers

from cover_house.cases.models import CoverSku
from cover_house.orders.models import (
    Address,
    Cart,
    CartItem,
    Order,
    OrderItem,
)


# ─── Address ─────────────────────────────────────────────────────────────────

class AddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = Address
        fields = [
            "id", "full_name", "phone",
            "province", "district", "city",
            "street_address", "landmark",
            "is_default",
        ]
        read_only_fields = ["id"]


# ─── Cart ────────────────────────────────────────────────────────────────────

class CartItemSerializer(serializers.ModelSerializer):
    cover_sku_id = serializers.UUIDField(source="cover_sku.id", read_only=True)
    sku_code = serializers.CharField(source="cover_sku.sku_code", read_only=True)
    cover_title = serializers.CharField(source="cover_sku.title", read_only=True)
    cover_slug = serializers.CharField(source="cover_sku.slug", read_only=True)
    phone_variant_name = serializers.CharField(
        source="cover_sku.phone_variant.name", read_only=True
    )
    color_name = serializers.CharField(
        source="cover_sku.color.name", read_only=True, default=""
    )
    unit_price = serializers.DecimalField(
        max_digits=10, decimal_places=2, read_only=True
    )
    line_total = serializers.DecimalField(
        max_digits=12, decimal_places=2, read_only=True
    )
    available_stock = serializers.IntegerField(
        source="cover_sku.stock_qty", read_only=True
    )

    class Meta:
        model = CartItem
        fields = [
            "id", "cover_sku_id", "sku_code",
            "cover_title", "cover_slug",
            "phone_variant_name", "color_name",
            "quantity", "unit_price", "line_total",
            "available_stock",
        ]
        read_only_fields = ["id"]


class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(many=True, read_only=True)
    subtotal = serializers.DecimalField(
        max_digits=12, decimal_places=2, read_only=True
    )
    item_count = serializers.SerializerMethodField()

    class Meta:
        model = Cart
        fields = ["id", "items", "item_count", "subtotal"]
        read_only_fields = fields

    def get_item_count(self, obj):
        return sum(i.quantity for i in obj.items.all())


class CartItemWriteSerializer(serializers.Serializer):
    """Used by POST /api/cart/items/ and PATCH /api/cart/items/{id}/."""
    cover_sku = serializers.UUIDField()
    quantity = serializers.IntegerField(min_value=1, default=1)

    def validate(self, attrs):
        try:
            sku = CoverSku.objects.get(
                id=attrs["cover_sku"], is_active=True, is_archived=False
            )
        except CoverSku.DoesNotExist as exc:
            raise serializers.ValidationError(
                {"cover_sku": "SKU not found or inactive."}
            ) from exc
        if sku.stock_qty < attrs["quantity"]:
            raise serializers.ValidationError(
                {"quantity": f"Only {sku.stock_qty} in stock."}
            )
        attrs["sku_obj"] = sku
        return attrs


# ─── Order ───────────────────────────────────────────────────────────────────

class OrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItem
        fields = [
            "id", "sku_code", "cover_title",
            "phone_variant_name", "color_name",
            "unit_price", "quantity", "line_total",
        ]
        read_only_fields = fields


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)

    class Meta:
        model = Order
        fields = [
            "id", "order_number",
            "status", "payment_status", "payment_method",
            "ship_full_name", "ship_phone",
            "ship_province", "ship_district", "ship_city",
            "ship_street_address", "ship_landmark",
            "subtotal", "shipping_fee", "discount_total", "grand_total",
            "customer_note",
            "placed_at", "paid_at", "shipped_at", "delivered_at", "cancelled_at",
            "items",
        ]
        read_only_fields = fields


# ─── Checkout ────────────────────────────────────────────────────────────────

class CheckoutSerializer(serializers.Serializer):
    """
    POST /api/checkout/

    Build an Order from the current user's Cart. Snapshots SKU info onto
    OrderItem rows and decrements stock atomically.
    """
    address_id = serializers.UUIDField(required=False)
    ship_full_name = serializers.CharField(max_length=120, required=False)
    ship_phone = serializers.CharField(max_length=20, required=False)
    ship_province = serializers.ChoiceField(
        choices=Address.Province.choices, required=False, allow_blank=True
    )
    ship_district = serializers.CharField(max_length=80, required=False)
    ship_city = serializers.CharField(max_length=80, required=False)
    ship_street_address = serializers.CharField(max_length=255, required=False)
    ship_landmark = serializers.CharField(
        max_length=120, required=False, allow_blank=True
    )

    payment_method = serializers.ChoiceField(
        choices=Order.PaymentMethod.choices, default=Order.PaymentMethod.COD
    )
    shipping_fee = serializers.DecimalField(
        max_digits=12, decimal_places=2, default=Decimal("0.00"), required=False
    )
    customer_note = serializers.CharField(required=False, allow_blank=True)

    def _resolve_ship_fields(self, user, attrs):
        if attrs.get("address_id"):
            try:
                addr = Address.objects.get(id=attrs["address_id"], user=user)
            except Address.DoesNotExist as exc:
                raise serializers.ValidationError(
                    {"address_id": "Address not found."}
                ) from exc
            return {
                "ship_full_name": addr.full_name,
                "ship_phone": addr.phone,
                "ship_province": addr.province,
                "ship_district": addr.district,
                "ship_city": addr.city,
                "ship_street_address": addr.street_address,
                "ship_landmark": addr.landmark,
            }

        required = [
            "ship_full_name", "ship_phone",
            "ship_district", "ship_city", "ship_street_address",
        ]
        missing = [f for f in required if not attrs.get(f)]
        if missing:
            raise serializers.ValidationError(
                {f: "This field is required." for f in missing}
            )
        return {f: attrs.get(f, "") for f in [
            "ship_full_name", "ship_phone", "ship_province",
            "ship_district", "ship_city", "ship_street_address", "ship_landmark",
        ]}

    def validate(self, attrs):
        user = self.context["request"].user
        try:
            cart = Cart.objects.prefetch_related("items__cover_sku").get(user=user)
        except Cart.DoesNotExist as exc:
            raise serializers.ValidationError("No active cart.") from exc
        if not cart.items.exists():
            raise serializers.ValidationError("Cart is empty.")
        attrs["cart"] = cart
        attrs["ship_fields"] = self._resolve_ship_fields(user, attrs)
        return attrs

    @transaction.atomic
    def create(self, validated_data):
        user = self.context["request"].user
        cart: Cart = validated_data["cart"]

        sku_ids = [item.cover_sku_id for item in cart.items.all()]
        skus = {
            s.id: s
            for s in CoverSku.objects.select_for_update()
            .select_related("phone_variant", "color")
            .filter(id__in=sku_ids)
        }

        subtotal = Decimal("0.00")
        items_payload = []
        for item in cart.items.all():
            sku = skus.get(item.cover_sku_id)
            if sku is None or not sku.is_active:
                raise serializers.ValidationError(
                    f"SKU no longer available: {item.cover_sku_id}"
                )
            if sku.stock_qty < item.quantity:
                raise serializers.ValidationError(
                    f"Insufficient stock for {sku.sku_code} "
                    f"({sku.stock_qty} left, {item.quantity} requested)."
                )
            unit_price = sku.effective_price
            line_total = unit_price * item.quantity
            subtotal += line_total
            items_payload.append((sku, item.quantity, unit_price, line_total))

        shipping_fee = validated_data.get("shipping_fee") or Decimal("0.00")
        grand_total = subtotal + shipping_fee

        order = Order.objects.create(
            user=user,
            payment_method=validated_data["payment_method"],
            subtotal=subtotal,
            shipping_fee=shipping_fee,
            grand_total=grand_total,
            customer_note=validated_data.get("customer_note", ""),
            **validated_data["ship_fields"],
        )

        for sku, qty, unit_price, line_total in items_payload:
            OrderItem.objects.create(
                order=order,
                cover_sku=sku,
                sku_code=sku.sku_code,
                cover_title=sku.title,
                phone_variant_name=str(sku.phone_variant),
                color_name=sku.color.name if sku.color_id else "",
                unit_price=unit_price,
                quantity=qty,
                line_total=line_total,
            )
            sku.stock_qty -= qty
            sku.save(update_fields=["stock_qty", "updated_at"])

        cart.items.all().delete()
        return order

    def to_representation(self, instance):
        return OrderSerializer(instance, context=self.context).data

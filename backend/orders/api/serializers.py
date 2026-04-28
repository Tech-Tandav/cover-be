from decimal import Decimal

from django.db import transaction
from rest_framework import serializers

from backend.catalog.models import Product
from backend.orders.models import Order, OrderItem


class OrderItemReadSerializer(serializers.ModelSerializer):
    product_id = serializers.IntegerField(source="product.id", read_only=True)
    subtotal = serializers.SerializerMethodField()

    class Meta:
        model = OrderItem
        fields = [
            "id",
            "product_id",
            "product_name",
            "product_image",
            "variant_color",
            "variant_size",
            "unit_price",
            "quantity",
            "subtotal",
        ]

    def get_subtotal(self, obj: OrderItem) -> Decimal:
        return obj.subtotal


class OrderItemWriteSerializer(serializers.Serializer):
    product_id = serializers.IntegerField()
    color = serializers.CharField(required=False, allow_blank=True, default="")
    size = serializers.CharField(required=False, allow_blank=True, default="")
    quantity = serializers.IntegerField(min_value=1)


class OrderReadSerializer(serializers.ModelSerializer):
    items = OrderItemReadSerializer(many=True, read_only=True)
    item_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Order
        fields = [
            "id",
            "order_number",
            "customer_name",
            "customer_phone",
            "customer_email",
            "shipping_address",
            "shipping_city",
            "items",
            "item_count",
            "subtotal",
            "shipping",
            "total",
            "status",
            "payment_method",
            "created_at",
        ]


class OrderCreateSerializer(serializers.ModelSerializer):
    items = OrderItemWriteSerializer(many=True, write_only=True)

    class Meta:
        model = Order
        fields = [
            "customer_name",
            "customer_phone",
            "customer_email",
            "shipping_address",
            "shipping_city",
            "shipping",
            "payment_method",
            "items",
        ]

    def validate_items(self, items):
        if not items:
            raise serializers.ValidationError("At least one item is required.")
        return items

    @transaction.atomic
    def create(self, validated_data):
        items_data = validated_data.pop("items")
        request = self.context.get("request")
        user = request.user if request and request.user.is_authenticated else None

        order = Order.objects.create(user=user, **validated_data)

        for item in items_data:
            try:
                product = (
                    Product.objects.select_for_update()
                    .get(pk=item["product_id"], is_active=True)
                )
            except Product.DoesNotExist as exc:
                raise serializers.ValidationError(
                    {"items": f"Product {item['product_id']} not found"}
                ) from exc

            if product.stock < item["quantity"]:
                raise serializers.ValidationError(
                    {
                        "items": (
                            f"Only {product.stock} of {product.name} in stock"
                        )
                    }
                )

            color = item.get("color", "")
            size = item.get("size", "")

            if color and color not in product.colors:
                raise serializers.ValidationError(
                    {"items": f"{product.name} is no longer available in {color}"}
                )
            if size and size not in product.sizes:
                raise serializers.ValidationError(
                    {"items": f"{product.name} is no longer available in size {size}"}
                )

            unit_price = product.discount_price or product.price
            try:
                product_image_url = product.image.url if product.image else ""
            except ValueError:
                product_image_url = ""

            OrderItem.objects.create(
                order=order,
                product=product,
                product_name=product.name,
                product_image=product_image_url,
                variant_color=color,
                variant_size=size,
                unit_price=unit_price,
                quantity=item["quantity"],
            )

            update_fields = ["stock"]
            product.stock = max(0, product.stock - item["quantity"])
            if color:
                product.colors = [c for c in product.colors if c != color]
                update_fields.append("colors")
            if size:
                product.sizes = [s for s in product.sizes if s != size]
                update_fields.append("sizes")
            product.save(update_fields=update_fields)

        order.recalc_totals()
        order.save(update_fields=["subtotal", "total"])
        return order


class OrderStatusUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ["status"]

from decimal import Decimal

from django.db import transaction
from rest_framework import serializers

from backend.catalog.models import Product, ProductType
from backend.orders.models import Order, OrderItem


class OrderItemReadSerializer(serializers.ModelSerializer):
    product_id = serializers.IntegerField(source="product.id", read_only=True)
    product_type_id = serializers.IntegerField(source="product_type.id", read_only=True, allow_null=True)
    subtotal = serializers.SerializerMethodField()

    class Meta:
        model = OrderItem
        fields = [
            "id",
            "product_id",
            "product_type_id",
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
    product_type_id = serializers.IntegerField(required=False, allow_null=True)
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
                product = Product.objects.get(pk=item["product_id"], is_active=True)
            except Product.DoesNotExist as exc:
                raise serializers.ValidationError(
                    {"items": f"Product {item['product_id']} not found"}
                ) from exc

            pt = None
            pt_id = item.get("product_type_id")
            if pt_id:
                try:
                    pt = ProductType.objects.get(
                        pk=pt_id, product=product, is_active=True
                    )
                except ProductType.DoesNotExist as exc:
                    raise serializers.ValidationError(
                        {"items": f"ProductType {pt_id} not found for product {product.id}"}
                    ) from exc
                if pt.stock < item["quantity"]:
                    raise serializers.ValidationError(
                        {
                            "items": (
                                f"Only {pt.stock} of {product.name} "
                                f"({pt.color}{f' / {pt.size}' if pt.size else ''}) in stock"
                            )
                        }
                    )
            elif product.types.filter(is_active=True).exists():
                raise serializers.ValidationError(
                    {
                        "items": (
                                f"{product.name} requires a color/size selection"
                        )
                    }
                )

            unit_price = product.discount_price or product.price
            ft = product.featured_type
            product_image_url = ""
            if ft and ft.image:
                try:
                    product_image_url = ft.image.url
                except ValueError:
                    pass
            OrderItem.objects.create(
                order=order,
                product=product,
                product_type=pt,
                product_name=product.name,
                product_image=product_image_url,
                variant_color=pt.color if pt else "",
                variant_size=pt.size if pt else "",
                unit_price=unit_price,
                quantity=item["quantity"],
            )
            if pt:
                pt.stock = max(0, pt.stock - item["quantity"])
                pt.save(update_fields=["stock"])

        order.recalc_totals()
        order.save(update_fields=["subtotal", "total"])
        return order


class OrderStatusUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ["status"]

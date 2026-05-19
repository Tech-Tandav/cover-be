from django.contrib import admin

from .models import Address, Cart, CartItem, Order, OrderItem


class CartItemInline(admin.TabularInline):
    model = CartItem
    extra = 0
    autocomplete_fields = ("cover_sku",)
    readonly_fields = ("created_at",)


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    autocomplete_fields = ("cover_sku",)
    readonly_fields = (
        "sku_code",
        "cover_title",
        "phone_variant_name",
        "color_name",
        "unit_price",
        "line_total",
    )


@admin.register(Address)
class AddressAdmin(admin.ModelAdmin):
    list_display = (
        "full_name",
        "user",
        "city",
        "district",
        "province",
        "is_default",
    )
    list_filter = ("province", "is_default")
    search_fields = ("full_name", "phone", "city", "district", "user__username")
    autocomplete_fields = ("user",)


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "session_key", "created_at")
    search_fields = ("user__username", "session_key")
    autocomplete_fields = ("user",)
    inlines = [CartItemInline]


@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    list_display = ("cart", "cover_sku", "sku_code", "quantity")
    search_fields = ("cart__id", "cover_sku__sku_code")
    autocomplete_fields = ("cart", "cover_sku")

    @admin.display(description="SKU code", ordering="cover_sku__sku_code")
    def sku_code(self, obj):
        return obj.cover_sku.sku_code


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = (
        "order_number",
        "user",
        "status",
        "payment_status",
        "payment_method",
        "grand_total",
        "placed_at",
    )
    list_filter = ("status", "payment_status", "payment_method")
    search_fields = (
        "order_number",
        "user__username",
        "ship_full_name",
        "ship_phone",
    )
    autocomplete_fields = ("user",)
    readonly_fields = (
        "order_number",
        "placed_at",
        "paid_at",
        "shipped_at",
        "delivered_at",
        "cancelled_at",
    )
    inlines = [OrderItemInline]


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ("order", "sku_code", "cover_title", "quantity", "line_total")
    search_fields = ("order__order_number", "sku_code", "cover_title")
    autocomplete_fields = ("order", "cover_sku")

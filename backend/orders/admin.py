from django.contrib import admin

from .models import Order, OrderItem


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ("product_name", "product_image", "unit_price", "quantity")
    can_delete = False


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = (
        "order_number",
        "customer_name",
        "customer_phone",
        "shipping_city",
        "total",
        "status",
        "payment_method",
        "created_at",
    )
    list_filter = ("status", "payment_method", "shipping_city", "created_at")
    list_editable = ("status",)
    search_fields = ("order_number", "customer_name", "customer_phone", "customer_email")
    readonly_fields = ("order_number", "subtotal", "total", "created_at", "updated_at")
    inlines = [OrderItemInline]
    date_hierarchy = "created_at"

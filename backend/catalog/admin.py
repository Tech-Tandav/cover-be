from django.contrib import admin

from .models import Category, Product, ProductImage


class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "slug", "is_featured", "sort_order", "created_at")
    list_editable = ("is_featured", "sort_order")
    prepopulated_fields = {"slug": ("name",)}
    search_fields = ("name", "slug")


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "brand",
        "category",
        "price",
        "discount_price",
        "stock",
        "is_active",
        "is_featured",
        "is_new",
    )
    list_filter = ("category", "brand", "type", "is_active", "is_featured", "is_new")
    list_editable = ("price", "discount_price", "stock", "is_active", "is_featured", "is_new")
    prepopulated_fields = {"slug": ("brand", "name")}
    search_fields = ("name", "brand", "slug", "description")
    inlines = [ProductImageInline]
    autocomplete_fields = ("category",)

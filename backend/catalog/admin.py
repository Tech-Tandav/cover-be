from django.contrib import admin

from .models import Brand, Category, Product, ProductImage, ProductType


class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1


@admin.register(Brand)
class BrandAdmin(admin.ModelAdmin):
    list_display = ("name", "slug", "is_active", "sort_order")
    list_editable = ("is_active", "sort_order")
    prepopulated_fields = {"slug": ("name",)}
    search_fields = ("name", "slug")


@admin.register(ProductType)
class ProductTypeAdmin(admin.ModelAdmin):
    list_display = ("name", "slug", "is_active", "sort_order")
    list_editable = ("is_active", "sort_order")
    prepopulated_fields = {"slug": ("name",)}
    search_fields = ("name", "slug")


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
    list_select_related = ("category", "brand", "type")
    list_editable = ("price", "discount_price", "stock", "is_active", "is_featured", "is_new")
    prepopulated_fields = {"slug": ("name",)}
    search_fields = ("name", "brand", "slug", "description")
    inlines = [ProductImageInline]
    autocomplete_fields = ("category", "brand", "type")

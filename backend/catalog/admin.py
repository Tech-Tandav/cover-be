from django.contrib import admin

from .models import Brand, Category, PhoneModel, Product, ProductImage, Variant


class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1


@admin.register(Brand)
class BrandAdmin(admin.ModelAdmin):
    list_display = ("name", "slug", "is_active", "sort_order")
    list_editable = ("is_active", "sort_order")
    prepopulated_fields = {"slug": ("name",)}
    search_fields = ("name", "slug")
    filter_horizontal = ("categories",)


@admin.register(PhoneModel)
class PhoneModelAdmin(admin.ModelAdmin):
    list_display = ("name", "brand", "slug", "is_active", "sort_order")
    list_editable = ("is_active", "sort_order")
    list_filter = ("brand", "is_active")
    list_select_related = ("brand",)
    search_fields = ("name", "slug", "brand__name")
    autocomplete_fields = ("brand",)


@admin.register(Variant)
class VariantAdmin(admin.ModelAdmin):
    list_display = ("name", "model", "slug", "is_active", "sort_order")
    list_editable = ("is_active", "sort_order")
    list_filter = ("model__brand", "model", "is_active")
    list_select_related = ("model", "model__brand")
    search_fields = ("name", "slug", "model__name", "model__brand__name")
    autocomplete_fields = ("model",)


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
    list_filter = ("category", "brand", "is_active", "is_featured", "is_new")
    list_select_related = ("category", "brand")
    list_editable = ("price", "discount_price", "stock", "is_active", "is_featured", "is_new")
    prepopulated_fields = {"slug": ("name",)}
    search_fields = ("name", "brand__name", "slug", "description")
    inlines = [ProductImageInline]
    autocomplete_fields = ("category", "brand")
    filter_horizontal = ("variants",)

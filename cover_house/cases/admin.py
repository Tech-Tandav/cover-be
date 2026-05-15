from django.contrib import admin

from .models import (
    CaseCategory,
    CaseColor,
    CoverImage,
    CoverSku,
)


class CoverImageInline(admin.TabularInline):
    model = CoverImage
    extra = 1
    fields = ("image", "alt_text", "is_primary", "sort_order")


@admin.register(CaseCategory)
class CaseCategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "sort_order", "is_archived")
    list_filter = ("is_archived",)
    search_fields = ("name",)
    prepopulated_fields = {"slug": ("name",)}


@admin.register(CaseColor)
class CaseColorAdmin(admin.ModelAdmin):
    list_display = ("name", "hex_code", "sort_order", "is_archived")
    list_filter = ("is_archived",)
    search_fields = ("name", "hex_code")
    prepopulated_fields = {"slug": ("name",)}


@admin.register(CoverSku)
class CoverSkuAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "sku_code",
        "phone_variant",
        "color",
        "category",
        "base_price",
        "discount_price",
        "stock_qty",
        "is_active",
    )
    list_filter = (
        "category",
        "phone_variant__phone_model__series__brand",
        "color",
        "is_active",
        "is_archived",
    )
    search_fields = (
        "title",
        "sku_code",
        "description",
        "phone_variant__name",
        "phone_variant__phone_model__name",
    )
    autocomplete_fields = ("category", "phone_variant", "color")
    prepopulated_fields = {"slug": ("title",)}
    inlines = [CoverImageInline]


@admin.register(CoverImage)
class CoverImageAdmin(admin.ModelAdmin):
    list_display = ("cover_sku", "is_primary", "sort_order")
    list_filter = ("is_primary",)
    search_fields = ("cover_sku__title", "cover_sku__sku_code")
    autocomplete_fields = ("cover_sku",)

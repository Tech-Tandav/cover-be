from django.contrib import admin

from .models import (
    CaseCategory,
    CaseColor,
    CoverImage,
    CoverSku,
    SiteSettings,
)


@admin.register(SiteSettings)
class SiteSettingsAdmin(admin.ModelAdmin):
    list_display = ("site_name", "tagline", "updated_at")

    def has_add_permission(self, request):
        return not SiteSettings.objects.exists()

    def has_delete_permission(self, request, obj=None):
        return False


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
        "phone_variant",
        "sku_code",
        "categories_display",
        "colors_display",
        "base_price",
        "discount_price",
        "stock_qty",
        "is_active",
    )
    list_filter = (
        "categories",
        "phone_variant__phone_model__series__brand",
        "colors",
        "is_active",
        "is_archived",
    )
    search_fields = (
        "sku_code",
        "description",
        "phone_variant__name",
        "phone_variant__phone_model__name",
    )
    autocomplete_fields = ("phone_variant",)
    filter_horizontal = ("categories", "colors")
    inlines = [CoverImageInline]

    @admin.display(description="Categories")
    def categories_display(self, obj):
        return ", ".join(c.name for c in obj.categories.all()) or "—"

    @admin.display(description="Colors")
    def colors_display(self, obj):
        return ", ".join(c.name for c in obj.colors.all()) or "—"


@admin.register(CoverImage)
class CoverImageAdmin(admin.ModelAdmin):
    list_display = ("cover_sku", "sku_code", "is_primary", "sort_order")
    list_filter = ("is_primary",)
    search_fields = ("cover_sku__title", "cover_sku__sku_code")
    autocomplete_fields = ("cover_sku",)

    @admin.display(description="SKU code", ordering="cover_sku__sku_code")
    def sku_code(self, obj):
        return obj.cover_sku.sku_code

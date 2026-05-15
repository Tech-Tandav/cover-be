from django.contrib import admin

from .models import Brand, PhoneModel, PhoneVariant, Series


@admin.register(Brand)
class BrandAdmin(admin.ModelAdmin):
    list_display = ("name",  "sort_order", "is_archived")
    list_filter = ("is_archived", )
    search_fields = ("name",)
    prepopulated_fields = {"slug": ("name",)}


@admin.register(Series)
class SeriesAdmin(admin.ModelAdmin):
    list_display = ("name", "brand", "sort_order", "is_archived")
    list_filter = ("brand", "is_archived")
    search_fields = ("name", "brand__name")
    autocomplete_fields = ("brand",)
    prepopulated_fields = {"slug": ("name",)}


@admin.register(PhoneModel)
class PhoneModelAdmin(admin.ModelAdmin):
    list_display = ("name", "series", "release_year", "is_archived")
    list_filter = ("series__brand", "release_year", "is_archived")
    search_fields = ("name", "series__name", "series__brand__name")
    autocomplete_fields = ("series",)
    prepopulated_fields = {"slug": ("name",)}


@admin.register(PhoneVariant)
class PhoneVariantAdmin(admin.ModelAdmin):
    list_display = ("name", "phone_model", "release_year", "is_active", "is_archived")
    list_filter = (
        "phone_model__series__brand",
        "is_active",
        "release_year",
        "is_archived",
    )
    search_fields = (
        "name",
        "phone_model__name",
        "phone_model__series__name",
        "phone_model__series__brand__name",
    )
    autocomplete_fields = ("phone_model",)
    prepopulated_fields = {"slug": ("name",)}

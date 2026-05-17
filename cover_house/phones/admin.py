from django.contrib import admin

from .models import Brand, PhoneModel, PhoneVariant, Series


class SeriesInline(admin.TabularInline):
    model = Series
    extra = 0
    fields = ("name", "slug", "sort_order", "is_archived")
    prepopulated_fields = {"slug": ("name",)}
    show_change_link = True


class PhoneModelInline(admin.TabularInline):
    model = PhoneModel
    extra = 0
    fields = ("name", "slug", "release_year", "sort_order", "is_archived")
    prepopulated_fields = {"slug": ("name",)}
    show_change_link = True


class PhoneVariantInline(admin.TabularInline):
    model = PhoneVariant
    extra = 0
    fields = ("name", "slug", "release_year", "is_active", "is_archived")
    prepopulated_fields = {"slug": ("name",)}
    show_change_link = True


@admin.register(Brand)
class BrandAdmin(admin.ModelAdmin):
    list_display = ("name", "sort_order", "is_archived")
    list_filter = ("is_archived",)
    search_fields = ("name",)
    prepopulated_fields = {"slug": ("name",)}
    inlines = [SeriesInline]


@admin.register(Series)
class SeriesAdmin(admin.ModelAdmin):
    list_display = ("name", "brand", "sort_order", "is_archived")
    list_filter = ("brand", "is_archived")
    search_fields = ("name", "brand__name")
    autocomplete_fields = ("brand",)
    prepopulated_fields = {"slug": ("name",)}
    inlines = [PhoneModelInline]


@admin.register(PhoneModel)
class PhoneModelAdmin(admin.ModelAdmin):
    list_display = ("name", "series", "release_year", "is_archived")
    list_filter = ("series__brand", "release_year", "is_archived")
    search_fields = ("name", "series__name", "series__brand__name")
    autocomplete_fields = ("series",)
    prepopulated_fields = {"slug": ("name",)}
    inlines = [PhoneVariantInline]


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

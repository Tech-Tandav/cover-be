from rest_framework import serializers

from cover_house.cases.models import (
    CaseCategory,
    CaseColor,
    CoverImage,
    CoverSku,
    SiteSettings,
)


class SiteSettingsSerializer(serializers.ModelSerializer):
    class Meta:
        model = SiteSettings
        fields = ["site_name", "tagline", "logo"]
        read_only_fields = fields


class CaseCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = CaseCategory
        fields = ["id", "name", "slug", "sort_order"]


class CaseColorSerializer(serializers.ModelSerializer):
    class Meta:
        model = CaseColor
        fields = ["id", "name", "slug", "hex_code", "sort_order"]


class CoverImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = CoverImage
        fields = ["id", "image", "alt_text", "is_primary", "sort_order"]


class CoverSkuListSerializer(serializers.ModelSerializer):
    """Lean payload for grids/listings."""
    phone_variant = serializers.SlugRelatedField(slug_field="slug", read_only=True)
    phone_variant_name = serializers.CharField(
        source="phone_variant.name", read_only=True
    )
    categories = CaseCategorySerializer(many=True, read_only=True)
    colors = CaseColorSerializer(many=True, read_only=True)
    primary_image = serializers.SerializerMethodField()
    effective_price = serializers.DecimalField(
        max_digits=10, decimal_places=2, read_only=True
    )
    is_on_sale = serializers.SerializerMethodField()
    in_stock = serializers.BooleanField(read_only=True)

    class Meta:
        model = CoverSku
        fields = [
            "id", "slug", "sku_code",
            "categories",
            "phone_variant", "phone_variant_name",
            "colors",
            "base_price", "discount_price", "effective_price", "is_on_sale",
            "stock_qty", "in_stock",
            "primary_image",
        ]

    def get_primary_image(self, obj):
        request = self.context.get("request")
        img = next(
            (i for i in obj.images.all() if i.is_primary),
            next(iter(obj.images.all()), None),
        )
        if not img:
            return None
        url = img.image.url
        return request.build_absolute_uri(url) if request else url

    def get_is_on_sale(self, obj):
        return obj.discount_price is not None


class CoverSkuDetailSerializer(serializers.ModelSerializer):
    """Full product page payload."""
    categories = CaseCategorySerializer(many=True, read_only=True)
    colors = CaseColorSerializer(many=True, read_only=True)
    phone_variant = serializers.SerializerMethodField()
    images = CoverImageSerializer(many=True, read_only=True)
    effective_price = serializers.DecimalField(
        max_digits=10, decimal_places=2, read_only=True
    )
    is_on_sale = serializers.SerializerMethodField()
    in_stock = serializers.BooleanField(read_only=True)

    class Meta:
        model = CoverSku
        fields = [
            "id", "slug", "sku_code",
            "description",
            "categories", "colors", "phone_variant",
            "base_price", "discount_price", "effective_price", "is_on_sale",
            "stock_qty", "in_stock", "fitment_notes",
            "is_active",
            "images",
            "created_at",
        ]

    def get_phone_variant(self, obj):
        from cover_house.phones.api.serializers import PhoneVariantSerializer
        return PhoneVariantSerializer(obj.phone_variant).data

    def get_is_on_sale(self, obj):
        return obj.discount_price is not None

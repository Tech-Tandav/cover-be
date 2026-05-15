from rest_framework import serializers

from cover_house.phones.models import Brand, PhoneModel, PhoneVariant, Series


class BrandSerializer(serializers.ModelSerializer):
    class Meta:
        model = Brand
        fields = ["id", "name", "slug", "logo", "sort_order"]


class SeriesSerializer(serializers.ModelSerializer):
    brand = serializers.SlugRelatedField(slug_field="slug", read_only=True)
    brand_name = serializers.CharField(source="brand.name", read_only=True)

    class Meta:
        model = Series
        fields = ["id", "name", "slug", "brand", "brand_name", "sort_order"]


class PhoneModelSerializer(serializers.ModelSerializer):
    series = serializers.SlugRelatedField(slug_field="slug", read_only=True)
    series_name = serializers.CharField(source="series.name", read_only=True)
    brand_slug = serializers.CharField(source="series.brand.slug", read_only=True)

    class Meta:
        model = PhoneModel
        fields = [
            "id", "name", "slug",
            "series", "series_name", "brand_slug",
            "release_year", "sort_order",
        ]


class PhoneVariantSerializer(serializers.ModelSerializer):
    phone_model = serializers.SlugRelatedField(slug_field="slug", read_only=True)
    model_name = serializers.CharField(source="phone_model.name", read_only=True)
    series_slug = serializers.CharField(source="phone_model.series.slug", read_only=True)
    brand_slug = serializers.CharField(
        source="phone_model.series.brand.slug", read_only=True
    )

    class Meta:
        model = PhoneVariant
        fields = [
            "id", "name", "slug",
            "phone_model", "model_name", "series_slug", "brand_slug",
            "release_year", "is_active",
        ]

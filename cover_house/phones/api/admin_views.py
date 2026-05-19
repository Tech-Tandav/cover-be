"""
Admin-only write API for the phone taxonomy. Mounted under /api/admin/.
"""
from rest_framework import serializers, viewsets
from rest_framework.permissions import IsAdminUser

from cover_house.phones.models import Brand, PhoneModel, PhoneVariant, Series


class BrandAdminSerializer(serializers.ModelSerializer):
    class Meta:
        model = Brand
        fields = [
            "id", "name", "slug", "logo",
            "sort_order", "is_archived",
        ]
        read_only_fields = ["id", "slug"]


class SeriesAdminSerializer(serializers.ModelSerializer):
    class Meta:
        model = Series
        fields = ["id", "name", "slug", "brand", "sort_order", "is_archived"]
        read_only_fields = ["id", "slug"]


class PhoneModelAdminSerializer(serializers.ModelSerializer):
    class Meta:
        model = PhoneModel
        fields = [
            "id", "name", "slug", "series",
            "release_year", "sort_order", "is_archived",
        ]
        read_only_fields = ["id", "slug"]


class PhoneVariantAdminSerializer(serializers.ModelSerializer):
    # full_name is denormalised and maintained by signals — return it lean
    # so dropdowns don't need to walk the nested chain.
    class Meta:
        model = PhoneVariant
        fields = [
            "id", "name", "slug", "full_name", "phone_model",
            "release_year", "is_active", "is_archived",
        ]
        read_only_fields = ["id", "slug", "full_name"]


class BrandAdminViewSet(viewsets.ModelViewSet):
    queryset = Brand.objects.all()
    serializer_class = BrandAdminSerializer
    permission_classes = [IsAdminUser]
    pagination_class = None
    lookup_field = "slug"


class SeriesAdminViewSet(viewsets.ModelViewSet):
    queryset = Series.objects.select_related("brand").all()
    serializer_class = SeriesAdminSerializer
    permission_classes = [IsAdminUser]
    pagination_class = None
    lookup_field = "slug"

    def get_queryset(self):
        qs = super().get_queryset()
        brand = self.request.query_params.get("brand")
        if brand:
            qs = qs.filter(brand__slug=brand)
        return qs


class PhoneModelAdminViewSet(viewsets.ModelViewSet):
    queryset = PhoneModel.objects.select_related("series__brand").all()
    serializer_class = PhoneModelAdminSerializer
    permission_classes = [IsAdminUser]
    pagination_class = None
    lookup_field = "slug"

    def get_queryset(self):
        qs = super().get_queryset()
        series = self.request.query_params.get("series")
        if series:
            qs = qs.filter(series__slug=series)
        return qs


class PhoneVariantAdminViewSet(viewsets.ModelViewSet):
    queryset = PhoneVariant.objects.select_related(
        "phone_model__series__brand"
    ).all()
    serializer_class = PhoneVariantAdminSerializer
    permission_classes = [IsAdminUser]
    pagination_class = None
    lookup_field = "slug"

    def get_queryset(self):
        qs = super().get_queryset()
        phone_model = self.request.query_params.get("phone_model")
        if phone_model:
            qs = qs.filter(phone_model__slug=phone_model)
        return qs

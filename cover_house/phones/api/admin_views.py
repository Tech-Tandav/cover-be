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
    class Meta:
        model = PhoneVariant
        fields = [
            "id", "name", "slug", "phone_model",
            "release_year", "is_active", "is_archived",
        ]
        read_only_fields = ["id", "slug"]


class BrandAdminViewSet(viewsets.ModelViewSet):
    queryset = Brand.objects.all()
    serializer_class = BrandAdminSerializer
    permission_classes = [IsAdminUser]
    lookup_field = "slug"


class SeriesAdminViewSet(viewsets.ModelViewSet):
    queryset = Series.objects.select_related("brand").all()
    serializer_class = SeriesAdminSerializer
    permission_classes = [IsAdminUser]
    lookup_field = "slug"


class PhoneModelAdminViewSet(viewsets.ModelViewSet):
    queryset = PhoneModel.objects.select_related("series__brand").all()
    serializer_class = PhoneModelAdminSerializer
    permission_classes = [IsAdminUser]
    lookup_field = "slug"


class PhoneVariantAdminViewSet(viewsets.ModelViewSet):
    queryset = PhoneVariant.objects.select_related(
        "phone_model__series__brand"
    ).all()
    serializer_class = PhoneVariantAdminSerializer
    permission_classes = [IsAdminUser]
    lookup_field = "slug"

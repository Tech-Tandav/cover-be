"""
Admin-only write API for covers. Mounted under /api/admin/.
"""
from rest_framework import serializers, viewsets
from rest_framework.permissions import IsAdminUser

from cover_house.cases.models import (
    CaseCategory,
    CaseColor,
    CoverImage,
    CoverSku,
)


class CaseCategoryAdminSerializer(serializers.ModelSerializer):
    class Meta:
        model = CaseCategory
        fields = ["id", "name", "slug", "sort_order", "is_archived"]
        read_only_fields = ["id", "slug"]


class CaseColorAdminSerializer(serializers.ModelSerializer):
    class Meta:
        model = CaseColor
        fields = ["id", "name", "slug", "hex_code", "sort_order", "is_archived"]
        read_only_fields = ["id", "slug"]


class CoverSkuAdminSerializer(serializers.ModelSerializer):
    class Meta:
        model = CoverSku
        fields = [
            "id", "title", "slug", "sku_code",
            "category", "phone_variant", "color",
            "description",
            "base_price", "discount_price",
            "stock_qty", "fitment_notes",
            "is_active", "is_archived",
        ]
        read_only_fields = ["id", "slug"]


class CoverImageAdminSerializer(serializers.ModelSerializer):
    class Meta:
        model = CoverImage
        fields = [
            "id", "cover_sku", "image",
            "alt_text", "is_primary", "sort_order",
        ]
        read_only_fields = ["id"]


class CaseCategoryAdminViewSet(viewsets.ModelViewSet):
    queryset = CaseCategory.objects.all()
    serializer_class = CaseCategoryAdminSerializer
    permission_classes = [IsAdminUser]
    lookup_field = "slug"


class CaseColorAdminViewSet(viewsets.ModelViewSet):
    queryset = CaseColor.objects.all()
    serializer_class = CaseColorAdminSerializer
    permission_classes = [IsAdminUser]
    lookup_field = "slug"


class CoverSkuAdminViewSet(viewsets.ModelViewSet):
    queryset = CoverSku.objects.select_related(
        "category", "phone_variant", "color"
    ).all()
    serializer_class = CoverSkuAdminSerializer
    permission_classes = [IsAdminUser]
    lookup_field = "slug"


class CoverImageAdminViewSet(viewsets.ModelViewSet):
    queryset = CoverImage.objects.select_related("cover_sku").all()
    serializer_class = CoverImageAdminSerializer
    permission_classes = [IsAdminUser]

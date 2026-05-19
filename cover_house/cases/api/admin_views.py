"""
Admin-only write API for covers. Mounted under /api/admin/.
"""
import secrets

from rest_framework import serializers, viewsets
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from rest_framework.views import APIView

from cover_house.cases.models import (
    CaseCategory,
    CaseColor,
    CoverImage,
    CoverSku,
    SiteSettings,
)


class SiteSettingsAdminSerializer(serializers.ModelSerializer):
    class Meta:
        model = SiteSettings
        fields = ["site_name", "tagline", "logo"]


class SiteSettingsAdminView(APIView):
    """
    GET   /api/admin/site-settings/   read current branding
    PATCH /api/admin/site-settings/   update site name / tagline / logo
    """
    permission_classes = [IsAdminUser]

    def get(self, request):
        obj = SiteSettings.load()
        return Response(
            SiteSettingsAdminSerializer(obj, context={"request": request}).data
        )

    def patch(self, request):
        obj = SiteSettings.load()
        ser = SiteSettingsAdminSerializer(
            obj, data=request.data, partial=True, context={"request": request}
        )
        ser.is_valid(raise_exception=True)
        ser.save()
        return Response(ser.data)


def _generate_sku_code() -> str:
    """Generate a unique SKU code like 'CV-AB12CD34'."""
    for _ in range(10):
        code = f"CV-{secrets.token_hex(4).upper()}"
        if not CoverSku.objects.filter(sku_code=code).exists():
            return code
    # Extremely unlikely fallback
    raise serializers.ValidationError("Could not allocate a unique SKU code.")


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
    sku_code = serializers.CharField(required=False, allow_blank=True)

    class Meta:
        model = CoverSku
        fields = [
            "id", "slug", "sku_code",
            "categories", "phone_variant", "colors",
            "description",
            "base_price", "discount_price",
            "stock_qty", "fitment_notes",
            "is_active", "is_archived",
        ]
        read_only_fields = ["id", "slug"]

    def create(self, validated_data):
        if not validated_data.get("sku_code"):
            validated_data["sku_code"] = _generate_sku_code()
        return super().create(validated_data)


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
        "phone_variant"
    ).prefetch_related("colors", "categories").all()
    serializer_class = CoverSkuAdminSerializer
    permission_classes = [IsAdminUser]
    lookup_field = "slug"


class CoverImageAdminViewSet(viewsets.ModelViewSet):
    queryset = CoverImage.objects.select_related("cover_sku").all()
    serializer_class = CoverImageAdminSerializer
    permission_classes = [IsAdminUser]

    def get_queryset(self):
        qs = super().get_queryset()
        cover_sku = self.request.query_params.get("cover_sku")
        if cover_sku:
            qs = qs.filter(cover_sku=cover_sku)
        return qs.order_by("sort_order", "created_at")

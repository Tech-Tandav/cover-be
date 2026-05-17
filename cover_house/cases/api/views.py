from rest_framework import viewsets
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from cover_house.cases.models import CaseCategory, CaseColor, CoverSku, SiteSettings

from .serializers import (
    CaseCategorySerializer,
    CaseColorSerializer,
    CoverSkuDetailSerializer,
    CoverSkuListSerializer,
    SiteSettingsSerializer,
)


class SiteSettingsView(APIView):
    """GET /api/site-settings/ — public storefront branding."""
    permission_classes = [AllowAny]

    def get(self, request):
        ser = SiteSettingsSerializer(
            SiteSettings.load(), context={"request": request}
        )
        return Response(ser.data)


class CaseCategoryViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = CaseCategory.objects.filter(is_archived=False)
    serializer_class = CaseCategorySerializer
    permission_classes = [AllowAny]
    lookup_field = "slug"


class CaseColorViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = CaseColor.objects.filter(is_archived=False)
    serializer_class = CaseColorSerializer
    permission_classes = [AllowAny]
    lookup_field = "slug"


class CoverSkuViewSet(viewsets.ReadOnlyModelViewSet):
    """
    GET /api/covers/
        ?phone_variant={slug}     filter to covers fitting this variant
        &phone_model={slug}        filter to covers fitting any variant of this model
        &category={slug,slug2,...} filter by cover category/categories; comma OR match
        &color={slug,slug2,...}   filter by colour(s); comma-separated OR match
        &min_price=&max_price=     price band
        &in_stock=true             only covers with stock
        &on_sale=true              only covers with a discount_price set

    GET /api/covers/{slug}/        full product detail
    """
    permission_classes = [AllowAny]
    lookup_field = "slug"

    def get_serializer_class(self):
        if self.action == "retrieve":
            return CoverSkuDetailSerializer
        return CoverSkuListSerializer

    def get_queryset(self):
        qs = (
            CoverSku.objects.filter(is_active=True, is_archived=False)
            .select_related("phone_variant")
            .prefetch_related("images", "categories", "colors")
        )

        p = self.request.query_params

        if p.get("phone_variant"):
            qs = qs.filter(phone_variant__slug=p["phone_variant"])
        if p.get("phone_model"):
            qs = qs.filter(phone_variant__phone_model__slug=p["phone_model"])
        if p.get("category"):
            cat_slugs = [s for s in p["category"].split(",") if s]
            if cat_slugs:
                qs = qs.filter(categories__slug__in=cat_slugs).distinct()
        if p.get("color"):
            color_slugs = [s for s in p["color"].split(",") if s]
            if color_slugs:
                qs = qs.filter(colors__slug__in=color_slugs).distinct()
        if p.get("min_price"):
            qs = qs.filter(base_price__gte=p["min_price"])
        if p.get("max_price"):
            qs = qs.filter(base_price__lte=p["max_price"])
        if p.get("in_stock") in {"true", "1"}:
            qs = qs.filter(stock_qty__gt=0)
        if p.get("on_sale") in {"true", "1"}:
            qs = qs.filter(discount_price__isnull=False)

        return qs

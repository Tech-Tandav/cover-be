from rest_framework import viewsets
from rest_framework.permissions import AllowAny

from cover_house.cases.models import CaseCategory, CaseColor, CoverSku

from .serializers import (
    CaseCategorySerializer,
    CaseColorSerializer,
    CoverSkuDetailSerializer,
    CoverSkuListSerializer,
)


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
        &category={slug}           filter by cover type
        &color={slug}              filter by colour
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
            .select_related("category", "phone_variant", "color")
            .prefetch_related("images")
        )

        p = self.request.query_params

        if p.get("phone_variant"):
            qs = qs.filter(phone_variant__slug=p["phone_variant"])
        if p.get("category"):
            qs = qs.filter(category__slug=p["category"])
        if p.get("color"):
            qs = qs.filter(color__slug=p["color"])
        if p.get("min_price"):
            qs = qs.filter(base_price__gte=p["min_price"])
        if p.get("max_price"):
            qs = qs.filter(base_price__lte=p["max_price"])
        if p.get("in_stock") in {"true", "1"}:
            qs = qs.filter(stock_qty__gt=0)
        if p.get("on_sale") in {"true", "1"}:
            qs = qs.filter(discount_price__isnull=False)

        return qs

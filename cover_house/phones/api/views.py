from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from cover_house.phones.models import Brand, PhoneModel, PhoneVariant, Series

from .serializers import (
    BrandSerializer,
    PhoneModelSerializer,
    PhoneVariantSerializer,
    SeriesSerializer,
)


class BrandViewSet(viewsets.ReadOnlyModelViewSet):
    """
    GET /api/brands/                list active brands
    GET /api/brands/{slug}/         brand detail
    GET /api/brands/{slug}/series/  series for this brand
    """
    queryset = Brand.objects.filter(is_archived=False)
    serializer_class = BrandSerializer
    permission_classes = [AllowAny]
    lookup_field = "slug"

    @action(detail=True, url_path="series")
    def list_series(self, request, slug=None):
        brand = self.get_object()
        qs = Series.objects.filter(brand=brand, is_archived=False)
        return Response(SeriesSerializer(qs, many=True).data)


class SeriesViewSet(viewsets.ReadOnlyModelViewSet):
    """
    GET /api/series/?brand={brand_slug}
    GET /api/series/{slug}/
    GET /api/series/{slug}/models/
    """
    serializer_class = SeriesSerializer
    permission_classes = [AllowAny]
    lookup_field = "slug"

    def get_queryset(self):
        qs = Series.objects.filter(is_archived=False).select_related("brand")
        brand_slug = self.request.query_params.get("brand")
        if brand_slug:
            qs = qs.filter(brand__slug=brand_slug)
        return qs

    @action(detail=True, url_path="models")
    def list_models(self, request, slug=None):
        series = self.get_object()
        qs = PhoneModel.objects.filter(series=series, is_archived=False)
        return Response(PhoneModelSerializer(qs, many=True).data)


class PhoneModelViewSet(viewsets.ReadOnlyModelViewSet):
    """
    GET /api/phone-models/?series={series_slug}
    GET /api/phone-models/{slug}/
    GET /api/phone-models/{slug}/variants/
    """
    serializer_class = PhoneModelSerializer
    permission_classes = [AllowAny]
    lookup_field = "slug"

    def get_queryset(self):
        qs = (
            PhoneModel.objects.filter(is_archived=False)
            .select_related("series", "series__brand")
        )
        series_slug = self.request.query_params.get("series")
        brand_slug = self.request.query_params.get("brand")
        if series_slug:
            qs = qs.filter(series__slug=series_slug)
        if brand_slug:
            qs = qs.filter(series__brand__slug=brand_slug)
        return qs

    @action(detail=True, url_path="variants")
    def list_variants(self, request, slug=None):
        phone_model = self.get_object()
        qs = PhoneVariant.objects.filter(
            phone_model=phone_model, is_archived=False, is_active=True
        )
        return Response(PhoneVariantSerializer(qs, many=True).data)


class PhoneVariantViewSet(viewsets.ReadOnlyModelViewSet):
    """
    GET /api/phone-variants/?phone_model={slug}
    GET /api/phone-variants/{slug}/
    GET /api/phone-variants/{slug}/covers/   -> see cases app
    """
    serializer_class = PhoneVariantSerializer
    permission_classes = [AllowAny]
    lookup_field = "slug"

    def get_queryset(self):
        qs = (
            PhoneVariant.objects.filter(is_archived=False, is_active=True)
            .select_related("phone_model", "phone_model__series", "phone_model__series__brand")
        )
        params = self.request.query_params
        if params.get("phone_model"):
            qs = qs.filter(phone_model__slug=params["phone_model"])
        if params.get("series"):
            qs = qs.filter(phone_model__series__slug=params["series"])
        if params.get("brand"):
            qs = qs.filter(phone_model__series__brand__slug=params["brand"])
        return qs

    @action(detail=True, url_path="covers")
    def list_covers(self, request, slug=None):
        # Defer to cases app serializer to avoid circular imports.
        from cover_house.cases.api.serializers import CoverSkuListSerializer
        from cover_house.cases.models import CoverSku

        variant = self.get_object()
        qs = (
            CoverSku.objects.filter(
                phone_variant=variant,
                is_active=True,
                is_archived=False,
            )
            .prefetch_related("images", "colors", "categories")
        )
        return Response(
            CoverSkuListSerializer(qs, many=True, context={"request": request}).data
        )

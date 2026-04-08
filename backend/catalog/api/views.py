from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, viewsets
from rest_framework.permissions import AllowAny, IsAdminUser

from backend.catalog.models import Brand, Category, PhoneModel, Product, Variant

from .serializers import (
    BrandSerializer,
    CategorySerializer,
    PhoneModelSerializer,
    ProductDetailSerializer,
    ProductListSerializer,
    ProductWriteSerializer,
    VariantSerializer,
)


class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    lookup_field = "slug"

    def get_permissions(self):
        if self.action in ("list", "retrieve"):
            return [AllowAny()]
        return [IsAdminUser()]


class BrandViewSet(viewsets.ModelViewSet):
    queryset = Brand.objects.all().prefetch_related("categories")
    serializer_class = BrandSerializer
    lookup_field = "slug"

    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = {
        "categories__slug": ["exact"],
        "is_active": ["exact"],
    }
    search_fields = ["name"]

    def get_permissions(self):
        if self.action in ("list", "retrieve"):
            return [AllowAny()]
        return [IsAdminUser()]

    def get_queryset(self):
        qs = super().get_queryset()
        if self.action in ("list", "retrieve") and not (
            self.request.user and self.request.user.is_staff
        ):
            qs = qs.filter(is_active=True)
        return qs.distinct()


class PhoneModelViewSet(viewsets.ModelViewSet):
    queryset = PhoneModel.objects.select_related("brand").all()
    serializer_class = PhoneModelSerializer

    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = {
        "brand__slug": ["exact"],
        "brand": ["exact"],
        "is_active": ["exact"],
    }
    search_fields = ["name"]

    def get_permissions(self):
        if self.action in ("list", "retrieve"):
            return [AllowAny()]
        return [IsAdminUser()]

    def get_queryset(self):
        qs = super().get_queryset()
        if self.action in ("list", "retrieve") and not (
            self.request.user and self.request.user.is_staff
        ):
            qs = qs.filter(is_active=True)
        return qs


class VariantViewSet(viewsets.ModelViewSet):
    queryset = Variant.objects.select_related("model", "model__brand").all()
    serializer_class = VariantSerializer

    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = {
        "model__slug": ["exact"],
        "model": ["exact"],
        "model__brand__slug": ["exact"],
        "is_active": ["exact"],
    }
    search_fields = ["name"]

    def get_permissions(self):
        if self.action in ("list", "retrieve"):
            return [AllowAny()]
        return [IsAdminUser()]

    def get_queryset(self):
        qs = super().get_queryset()
        if self.action in ("list", "retrieve") and not (
            self.request.user and self.request.user.is_staff
        ):
            qs = qs.filter(is_active=True)
        return qs


class ProductViewSet(viewsets.ModelViewSet):
    queryset = (
        Product.objects.select_related("category", "brand")
        .prefetch_related("images", "variants")
    )
    lookup_field = "slug"

    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = {
        "category__slug": ["exact"],
        "brand__name": ["exact"],
        "brand__slug": ["exact"],
        "variants__slug": ["exact"],
        "variants__name": ["exact"],
        "material": ["exact"],
        "is_featured": ["exact"],
        "is_new": ["exact"],
        "is_active": ["exact"],
        "price": ["gte", "lte"],
    }
    search_fields = ["name", "brand__name", "description"]
    ordering_fields = ["created_at", "price", "rating"]
    ordering = ["-created_at"]

    def get_permissions(self):
        if self.action in ("list", "retrieve"):
            return [AllowAny()]
        return [IsAdminUser()]

    def get_serializer_class(self):
        if self.action == "list":
            return ProductListSerializer
        if self.action in ("create", "update", "partial_update"):
            return ProductWriteSerializer
        return ProductDetailSerializer

    def get_queryset(self):
        qs = super().get_queryset()
        # Public listings only show active products; admins see everything.
        if self.action in ("list", "retrieve") and not (
            self.request.user and self.request.user.is_staff
        ):
            qs = qs.filter(is_active=True)
        return qs.distinct()

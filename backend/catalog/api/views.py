from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, viewsets
from rest_framework.permissions import AllowAny, IsAdminUser

from backend.catalog.models import Category, Product

from .serializers import (
    CategorySerializer,
    ProductDetailSerializer,
    ProductListSerializer,
    ProductWriteSerializer,
)


class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    lookup_field = "slug"

    def get_permissions(self):
        if self.action in ("list", "retrieve"):
            return [AllowAny()]
        return [IsAdminUser()]


class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.select_related("category").prefetch_related("images")
    lookup_field = "slug"

    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = {
        "category__slug": ["exact"],
        "brand": ["exact"],
        "type": ["exact"],
        "material": ["exact"],
        "is_featured": ["exact"],
        "is_new": ["exact"],
        "is_active": ["exact"],
        "price": ["gte", "lte"],
    }
    search_fields = ["name", "brand", "description"]
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
        return qs

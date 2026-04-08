from rest_framework import serializers

from backend.catalog.models import Brand, Category, Product, ProductImage, Variant

PLACEHOLDER_IMAGE = (
    "https://images.unsplash.com/photo-1592286927505-1def25115558?w=800&q=80"
)


def _absolute_image_url(request, image_field) -> str:
    """Return an absolute URL for an ImageField, or a placeholder if missing."""
    if not image_field:
        return PLACEHOLDER_IMAGE
    url = image_field.url
    if request is not None:
        return request.build_absolute_uri(url)
    return url


class CategorySerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()
    product_count = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = [
            "id",
            "name",
            "slug",
            "description",
            "icon",
            "image",
            "product_count",
            "is_featured",
        ]

    def get_product_count(self, obj: Category) -> int:
        return obj.products.filter(is_active=True).count()

    def get_image(self, obj: Category) -> str:
        return _absolute_image_url(self.context.get("request"), obj.image)


class ProductImageSerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()

    class Meta:
        model = ProductImage
        fields = ["id", "image", "alt"]

    def get_image(self, obj: ProductImage) -> str:
        return _absolute_image_url(self.context.get("request"), obj.image)


class BrandSerializer(serializers.ModelSerializer):
    logo = serializers.SerializerMethodField()
    product_count = serializers.SerializerMethodField()
    category_slugs = serializers.SerializerMethodField()
    categories = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Category.objects.all(),
        required=False,
        write_only=True,
    )

    class Meta:
        model = Brand
        fields = [
            "id",
            "name",
            "slug",
            "logo",
            "categories",
            "category_slugs",
            "sort_order",
            "is_active",
            "product_count",
        ]
        read_only_fields = ["id", "slug", "product_count", "category_slugs"]

    def get_logo(self, obj: Brand) -> str | None:
        if not obj.logo:
            return None
        request = self.context.get("request")
        return request.build_absolute_uri(obj.logo.url) if request else obj.logo.url

    def get_product_count(self, obj: Brand) -> int:
        return obj.products.filter(is_active=True).count()

    def get_category_slugs(self, obj: Brand) -> list[str]:
        return list(obj.categories.values_list("slug", flat=True))


class VariantSerializer(serializers.ModelSerializer):
    brand_slug = serializers.SlugField(source="brand.slug", read_only=True)
    brand_name = serializers.CharField(source="brand.name", read_only=True)

    class Meta:
        model = Variant
        fields = [
            "id",
            "name",
            "slug",
            "brand",
            "brand_slug",
            "brand_name",
            "sort_order",
            "is_active",
        ]
        read_only_fields = ["id", "slug", "brand_slug", "brand_name"]


class ProductListSerializer(serializers.ModelSerializer):
    category = serializers.CharField(source="category.name", read_only=True)
    category_slug = serializers.SlugField(source="category.slug", read_only=True)
    brand = serializers.CharField(source="brand.name", read_only=True)
    brand_slug = serializers.SlugField(source="brand.slug", read_only=True)
    variants = serializers.SerializerMethodField()
    image = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = [
            "id",
            "name",
            "slug",
            "brand",
            "brand_slug",
            "category",
            "category_slug",
            "variants",
            "material",
            "color",
            "price",
            "discount_price",
            "stock",
            "image",
            "rating",
            "review_count",
            "is_featured",
            "is_new",
            "created_at",
        ]

    def get_image(self, obj: Product) -> str:
        return _absolute_image_url(self.context.get("request"), obj.image)

    def get_variants(self, obj: Product) -> list[str]:
        return [v.name for v in obj.variants.all()]


class ProductDetailSerializer(serializers.ModelSerializer):
    category = serializers.CharField(source="category.name", read_only=True)
    category_slug = serializers.SlugField(source="category.slug", read_only=True)
    brand = serializers.CharField(source="brand.name", read_only=True)
    brand_slug = serializers.SlugField(source="brand.slug", read_only=True)
    variants = serializers.SerializerMethodField()
    images = ProductImageSerializer(many=True, read_only=True)
    image = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = [
            "id",
            "name",
            "slug",
            "brand",
            "brand_slug",
            "category",
            "category_slug",
            "variants",
            "material",
            "color",
            "price",
            "discount_price",
            "stock",
            "description",
            "image",
            "images",
            "rating",
            "review_count",
            "is_featured",
            "is_new",
            "created_at",
        ]

    def get_image(self, obj: Product) -> str:
        return _absolute_image_url(self.context.get("request"), obj.image)

    def get_variants(self, obj: Product) -> list[str]:
        return [v.name for v in obj.variants.all()]


class ProductWriteSerializer(serializers.ModelSerializer):
    """For create/update from the dashboard."""

    brand = serializers.SlugRelatedField(
        slug_field="name",
        queryset=Brand.objects.filter(is_active=True),
    )
    variants = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Variant.objects.filter(is_active=True),
        required=False,
    )

    class Meta:
        model = Product
        fields = [
            "id",
            "category",
            "name",
            "slug",
            "brand",
            "variants",
            "material",
            "color",
            "price",
            "discount_price",
            "stock",
            "description",
            "image",
            "is_featured",
            "is_new",
            "is_active",
        ]
        read_only_fields = ["id", "slug"]

    def validate(self, attrs):
        """Ensure all chosen variants belong to the chosen brand."""
        brand = attrs.get("brand") or getattr(self.instance, "brand", None)
        variants = attrs.get("variants")
        if brand and variants:
            mismatched = [v for v in variants if v.brand_id != brand.id]
            if mismatched:
                names = ", ".join(v.name for v in mismatched)
                raise serializers.ValidationError(
                    {"variants": f"Variants do not belong to {brand.name}: {names}"}
                )
        return attrs

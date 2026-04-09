from rest_framework import serializers

from django.db import transaction

from backend.catalog.models import (
    Brand,
    Category,
    PhoneModel,
    Product,
    ProductImage,
    ProductSku,
    Variant,
)

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


class ProductSkuSerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()
    in_stock = serializers.SerializerMethodField()

    class Meta:
        model = ProductSku
        fields = [
            "id",
            "color",
            "size",
            "sku_code",
            "stock",
            "in_stock",
            "image",
            "is_active",
            "sort_order",
        ]
        read_only_fields = ["id", "sku_code", "in_stock"]

    def get_image(self, obj: ProductSku) -> str | None:
        if not obj.image:
            return None
        return _absolute_image_url(self.context.get("request"), obj.image)

    def get_in_stock(self, obj: ProductSku) -> bool:
        return obj.is_active and obj.stock > 0


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


class PhoneModelSerializer(serializers.ModelSerializer):
    brand_slug = serializers.SlugField(source="brand.slug", read_only=True)
    brand_name = serializers.CharField(source="brand.name", read_only=True)

    class Meta:
        model = PhoneModel
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


class VariantSerializer(serializers.ModelSerializer):
    model_slug = serializers.SlugField(source="model.slug", read_only=True)
    model_name = serializers.CharField(source="model.name", read_only=True)
    brand_id = serializers.IntegerField(source="model.brand_id", read_only=True)
    brand_slug = serializers.SlugField(source="model.brand.slug", read_only=True)
    brand_name = serializers.CharField(source="model.brand.name", read_only=True)

    class Meta:
        model = Variant
        fields = [
            "id",
            "name",
            "slug",
            "model",
            "model_slug",
            "model_name",
            "brand_id",
            "brand_slug",
            "brand_name",
            "sort_order",
            "is_active",
        ]
        read_only_fields = [
            "id",
            "slug",
            "model_slug",
            "model_name",
            "brand_id",
            "brand_slug",
            "brand_name",
        ]


class ProductListSerializer(serializers.ModelSerializer):
    category = serializers.CharField(source="category.name", read_only=True)
    category_slug = serializers.SlugField(source="category.slug", read_only=True)
    brand = serializers.CharField(source="brand.name", read_only=True)
    brand_slug = serializers.SlugField(source="brand.slug", read_only=True)
    variants = serializers.SerializerMethodField()
    image = serializers.SerializerMethodField()
    skus = ProductSkuSerializer(many=True, read_only=True)
    total_stock = serializers.IntegerField(read_only=True)

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
            "total_stock",
            "skus",
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
    skus = ProductSkuSerializer(many=True, read_only=True)
    total_stock = serializers.IntegerField(read_only=True)

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
            "total_stock",
            "skus",
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


class ProductSkuWriteSerializer(serializers.Serializer):
    """SKU rows are written nested under a Product. Only color/size/stock —
    price always lives on the parent Product."""

    color = serializers.CharField(max_length=80)
    size = serializers.CharField(max_length=40, allow_blank=True, required=False)
    stock = serializers.IntegerField(min_value=0)
    is_active = serializers.BooleanField(required=False, default=True)


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
    skus = ProductSkuWriteSerializer(many=True, required=False)

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
            "skus",
            "description",
            "image",
            "is_featured",
            "is_new",
            "is_active",
        ]
        read_only_fields = ["id", "slug"]

    def to_internal_value(self, data):
        """``skus`` may arrive as a JSON string when posted via multipart
        FormData (which is how the dashboard product form submits images).
        Decode it before normal field processing."""
        if hasattr(data, "getlist"):
            raw = data.get("skus")
            if isinstance(raw, str) and raw:
                import json

                try:
                    parsed = json.loads(raw)
                except json.JSONDecodeError as exc:
                    raise serializers.ValidationError(
                        {"skus": "Invalid JSON for skus field."}
                    ) from exc
                # QueryDict is immutable; mutate a copy.
                data = data.copy()
                data.setlist("skus", [])
                attrs = super().to_internal_value(data)
                attrs["skus"] = ProductSkuWriteSerializer(
                    data=parsed, many=True
                ).run_validation(parsed)
                return attrs
        return super().to_internal_value(data)

    def validate(self, attrs):
        """Ensure all chosen variants belong to a model under the chosen brand,
        and that all variants belong to the same model. SKU rows must have
        unique (color, size) combinations."""
        brand = attrs.get("brand") or getattr(self.instance, "brand", None)
        variants = attrs.get("variants")
        if brand and variants:
            mismatched = [v for v in variants if v.model.brand_id != brand.id]
            if mismatched:
                names = ", ".join(v.name for v in mismatched)
                raise serializers.ValidationError(
                    {"variants": f"Variants do not belong to {brand.name}: {names}"}
                )
            model_ids = {v.model_id for v in variants}
            if len(model_ids) > 1:
                raise serializers.ValidationError(
                    {"variants": "All variants must belong to the same model."}
                )

        skus = attrs.get("skus")
        if skus:
            seen: set[tuple[str, str]] = set()
            for row in skus:
                key = (row["color"].strip().lower(), (row.get("size") or "").strip().lower())
                if key in seen:
                    raise serializers.ValidationError(
                        {"skus": f"Duplicate (color, size) row: {row['color']} / {row.get('size') or '—'}"}
                    )
                seen.add(key)
        return attrs

    @transaction.atomic
    def create(self, validated_data):
        skus = validated_data.pop("skus", None)
        product = super().create(validated_data)
        if skus:
            for row in skus:
                ProductSku.objects.create(product=product, **row)
        return product

    @transaction.atomic
    def update(self, instance, validated_data):
        skus = validated_data.pop("skus", None)
        product = super().update(instance, validated_data)
        if skus is not None:
            # Replace the full SKU set on update — simplest semantics for the
            # dashboard form, which always sends the canonical list.
            existing = {(s.color, s.size): s for s in product.skus.all()}
            seen_keys: set[tuple[str, str]] = set()
            for row in skus:
                key = (row["color"], row.get("size", ""))
                seen_keys.add(key)
                if key in existing:
                    sku = existing[key]
                    sku.stock = row["stock"]
                    sku.is_active = row.get("is_active", True)
                    sku.save(update_fields=["stock", "is_active"])
                else:
                    ProductSku.objects.create(product=product, **row)
            for key, sku in existing.items():
                if key not in seen_keys:
                    sku.delete()
        return product

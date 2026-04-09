from django.db import models
from django.utils.text import slugify


class Category(models.Model):
    name = models.CharField(max_length=120, unique=True)
    slug = models.SlugField(max_length=140, unique=True, blank=True)
    description = models.TextField(blank=True, default="")
    icon = models.CharField(
        max_length=60,
        blank=True,
        default="",
        help_text="Lucide icon name used by the frontend (e.g. 'Smartphone').",
    )
    image = models.ImageField(upload_to="categories/", blank=True, null=True)
    is_featured = models.BooleanField(default=False)
    sort_order = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["sort_order", "name"]
        verbose_name_plural = "Categories"

    def __str__(self) -> str:
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class Brand(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=120, unique=True, blank=True)
    logo = models.ImageField(upload_to="brands/", blank=True, null=True)
    categories = models.ManyToManyField(
        Category,
        related_name="brands",
        blank=True,
        help_text="Categories this brand appears in. Used to filter the brand "
        "dropdown in the product form once a category is selected.",
    )
    sort_order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["sort_order", "name"]

    def __str__(self) -> str:
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class PhoneModel(models.Model):
    """A device model line under a brand, e.g. ``iPhone 16``, ``Galaxy S23``.
    Variants belong to a model, and a model belongs to a brand."""

    brand = models.ForeignKey(
        Brand,
        on_delete=models.CASCADE,
        related_name="phone_models",
    )
    name = models.CharField(max_length=120)
    slug = models.SlugField(max_length=160, blank=True)
    sort_order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["brand__name", "sort_order", "name"]
        constraints = [
            models.UniqueConstraint(
                fields=["brand", "name"], name="phonemodel_unique_per_brand"
            ),
            models.UniqueConstraint(
                fields=["brand", "slug"], name="phonemodel_slug_unique_per_brand"
            ),
        ]

    def __str__(self) -> str:
        return f"{self.brand.name} {self.name}"

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)[:160]
        super().save(*args, **kwargs)


class Variant(models.Model):
    """A specific device variant under a phone model, e.g. ``16 Plus`` and
    ``16 Pro Max`` under ``iPhone 16``. Products link to one or more variants
    to express compatibility."""

    model = models.ForeignKey(
        PhoneModel,
        on_delete=models.CASCADE,
        related_name="variants",
    )
    name = models.CharField(max_length=120)
    slug = models.SlugField(max_length=160, blank=True)
    sort_order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["model__brand__name", "model__name", "sort_order", "name"]
        constraints = [
            models.UniqueConstraint(
                fields=["model", "name"], name="variant_unique_per_model"
            ),
            models.UniqueConstraint(
                fields=["model", "slug"], name="variant_slug_unique_per_model"
            ),
        ]

    def __str__(self) -> str:
        return f"{self.model} {self.name}"

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)[:160]
        super().save(*args, **kwargs)


class Store(models.Model):
    name = models.CharField(max_length=120, unique=True)
    slug = models.SlugField(max_length=140, unique=True, blank=True)
    location = models.CharField(max_length=200, blank=True, default="")
    address = models.TextField(blank=True, default="")
    phone = models.CharField(max_length=40, blank=True, default="")
    email = models.EmailField(blank=True, default="")
    logo = models.ImageField(upload_to="stores/", blank=True, null=True)
    sort_order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["sort_order", "name"]

    def __str__(self) -> str:
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class Product(models.Model):
    category = models.ForeignKey(
        Category,
        on_delete=models.PROTECT,
        related_name="products",
    )
    name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=220, unique=True, blank=True)
    brand = models.ForeignKey(
        Brand,
        on_delete=models.PROTECT,
        related_name="products",
    )
    store = models.ForeignKey(
        Store,
        on_delete=models.PROTECT,
        related_name="products",
        null=True,
        blank=True,
    )
    variants = models.ManyToManyField(
        Variant,
        related_name="products",
        blank=True,
        help_text="Device variants this product is compatible with.",
    )
    material = models.CharField(max_length=80, blank=True, default="")

    price = models.DecimalField(max_digits=10, decimal_places=2)
    discount_price = models.DecimalField(
        max_digits=10, decimal_places=2, blank=True, null=True
    )

    description = models.TextField(blank=True, default="")

    rating = models.DecimalField(max_digits=3, decimal_places=2, default=0)
    review_count = models.PositiveIntegerField(default=0)

    hot_sale_live = models.BooleanField(
        default=False,
        help_text="Show this product in the Hot Sale section on the landing page.",
    )
    is_new = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["category", "is_active"]),
            models.Index(fields=["hot_sale_live"]),
        ]

    def __str__(self) -> str:
        return f"{self.brand} — {self.name}"

    def save(self, *args, **kwargs):
        if not self.slug:
            base = slugify(f"{self.brand}-{self.name}")[:200]
            self.slug = base
        super().save(*args, **kwargs)

    @property
    def featured_type(self):
        """Return the first active ProductType, used as the representative
        variant wherever the Product itself is displayed (listing image, etc.)."""
        return self.types.filter(is_active=True).first()

    @property
    def total_stock(self) -> int:
        """Total quantity across all active ProductType rows."""
        return sum(t.stock for t in self.types.filter(is_active=True))

    @property
    def available_colors(self) -> list[str]:
        seen: list[str] = []
        for t in self.types.filter(is_active=True):
            if t.color and t.color not in seen:
                seen.append(t.color)
        return seen

    @property
    def available_sizes(self) -> list[str]:
        seen: list[str] = []
        for t in self.types.filter(is_active=True):
            if t.size and t.size not in seen:
                seen.append(t.size)
        return seen


class ProductType(models.Model):
    """A specific (color, size) variation of a Product. Each ProductType carries
    its own color, image, and stock. The total quantity of all active
    ProductType rows equals the overall quantity of the parent Product."""

    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name="types",
    )
    color = models.CharField(max_length=80)
    size = models.CharField(
        max_length=40,
        blank=True,
        default="",
        help_text="Empty for products that don't have a size axis (e.g. cases "
        "that fit only one device variant).",
    )
    sku_code = models.CharField(max_length=64, unique=True, blank=True)
    stock = models.PositiveIntegerField(default=0)
    image = models.ImageField(upload_to="products/types/", blank=True, null=True)
    is_active = models.BooleanField(default=True)
    sort_order = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["product_id", "sort_order", "color", "size"]
        constraints = [
            models.UniqueConstraint(
                fields=["product", "color", "size"],
                name="producttype_unique_color_size_per_product",
            ),
        ]

    def __str__(self) -> str:
        bits = [self.color]
        if self.size:
            bits.append(self.size)
        return f"{self.product.name} — {' / '.join(bits)}"

    def save(self, *args, **kwargs):
        if not self.sku_code:
            base = slugify(
                f"{self.product_id}-{self.color}-{self.size or 'one'}"
            )[:60]
            candidate = base
            i = 1
            while (
                ProductType.objects.filter(sku_code=candidate)
                .exclude(pk=self.pk)
                .exists()
            ):
                i += 1
                candidate = f"{base}-{i}"
            self.sku_code = candidate
        super().save(*args, **kwargs)


class ProductImage(models.Model):
    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, related_name="images"
    )
    image = models.ImageField(upload_to="products/gallery/")
    alt = models.CharField(max_length=160, blank=True, default="")
    sort_order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["sort_order"]

    def __str__(self) -> str:
        return f"{self.product.name} — image {self.id}"

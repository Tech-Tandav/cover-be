"""
Seed the catalog with realistic e-commerce data for E-Store and Accessories.

Usage (inside Docker):
    docker compose -f docker-compose.local.yml run --rm django \\
        python manage.py seed_catalog

Re-running clears existing categories and products.
"""
from decimal import Decimal

from django.core.management.base import BaseCommand
from django.db import transaction

from backend.catalog.models import Brand, Category, PhoneModel, Product, Variant

CATEGORIES = [
    {
        "name": "Mobile Covers",
        "slug": "mobile-covers",
        "description": "Premium back covers and cases for all major phone brands",
        "icon": "Smartphone",
        "is_featured": True,
        "sort_order": 1,
    },
    {
        "name": "Screen Protectors",
        "slug": "screen-protectors",
        "description": "Tempered glass and matte protectors that actually last",
        "icon": "ShieldCheck",
        "is_featured": True,
        "sort_order": 2,
    },
    {
        "name": "Chargers & Cables",
        "slug": "chargers",
        "description": "Fast chargers, GaN adapters, USB-C and Lightning cables",
        "icon": "Zap",
        "is_featured": True,
        "sort_order": 3,
    },
    {
        "name": "Earbuds & Headphones",
        "slug": "earbuds",
        "description": "Wireless earbuds, ANC headphones, gaming headsets",
        "icon": "Headphones",
        "is_featured": True,
        "sort_order": 4,
    },
    {
        "name": "Smart Watches",
        "slug": "smart-watches",
        "description": "Fitness trackers and smart watches from top brands",
        "icon": "Watch",
        "is_featured": False,
        "sort_order": 5,
    },
    {
        "name": "Power Banks",
        "slug": "power-banks",
        "description": "10000mAh to 30000mAh fast charging power banks",
        "icon": "BatteryCharging",
        "is_featured": False,
        "sort_order": 6,
    },
    {
        "name": "Speakers",
        "slug": "speakers",
        "description": "Bluetooth speakers and portable sound systems",
        "icon": "Speaker",
        "is_featured": False,
        "sort_order": 7,
    },
    {
        "name": "Phone Holders",
        "slug": "phone-holders",
        "description": "Car mounts, desk stands, ring holders and grips",
        "icon": "Anchor",
        "is_featured": False,
        "sort_order": 8,
    },
]

PRODUCTS = [
    # Mobile Covers
    {
        "category": "mobile-covers",
        "name": "Carbon Fiber Armor Case",
        "brand": "Spigen",
        "type": "Rugged",
        "material": "TPU + Polycarbonate",
        "color": "Matte Black",
        "compatible_with": ["iPhone 15 Pro"],
        "price": "2499",
        "discount_price": "1899",
        "stock": 24,
        "rating": "4.7",
        "review_count": 128,
        "is_featured": True,
        "description": "Military-grade drop protection with raised bezels around the camera and screen.",
    },
    {
        "category": "mobile-covers",
        "name": "Liquid Silicone Soft Case",
        "brand": "Apple Style",
        "type": "Slim",
        "material": "Silicone",
        "color": "Midnight Blue",
        "compatible_with": ["Samsung Galaxy S24 Ultra"],
        "price": "1499",
        "discount_price": "1199",
        "stock": 41,
        "rating": "4.5",
        "review_count": 86,
        "is_featured": True,
        "is_new": True,
        "description": "Silky smooth silicone exterior with microfiber lining inside.",
    },
    {
        "category": "mobile-covers",
        "name": "Clear Shockproof Case",
        "brand": "ESR",
        "type": "Transparent",
        "material": "TPU",
        "color": "Crystal Clear",
        "compatible_with": ["iPhone 14", "iPhone 14 Plus"],
        "price": "999",
        "stock": 60,
        "rating": "4.3",
        "review_count": 54,
        "description": "Anti-yellowing crystal clear case with reinforced air-cushion corners.",
    },
    {
        "category": "mobile-covers",
        "name": "MagSafe Leather Wallet Case",
        "brand": "Nillkin",
        "type": "Wallet",
        "material": "Leather",
        "color": "Saddle Brown",
        "compatible_with": ["iPhone 15", "iPhone 15 Pro"],
        "price": "3299",
        "discount_price": "2799",
        "stock": 18,
        "rating": "4.8",
        "review_count": 45,
        "is_featured": True,
        "is_new": True,
        "description": "Genuine leather with MagSafe magnets and a slot for two cards.",
    },
    {
        "category": "mobile-covers",
        "name": "Aramid Fiber Premium Case",
        "brand": "Pitaka",
        "type": "Rugged",
        "material": "Aramid Fiber",
        "color": "Black/Grey Twill",
        "compatible_with": ["iPhone 15 Pro Max"],
        "price": "5999",
        "discount_price": "4999",
        "stock": 8,
        "rating": "4.9",
        "review_count": 31,
        "is_featured": True,
        "is_new": True,
        "description": "Aerospace-grade aramid fiber. Lighter than air, stronger than steel.",
    },
    # Screen Protectors
    {
        "category": "screen-protectors",
        "name": "9H Tempered Glass Protector",
        "brand": "Spigen",
        "type": "Tempered Glass",
        "material": "Glass",
        "color": "Clear",
        "compatible_with": ["iPhone 15"],
        "price": "599",
        "discount_price": "449",
        "stock": 120,
        "rating": "4.6",
        "review_count": 210,
        "is_featured": True,
        "description": "9H hardness with oleophobic coating. Bubble-free installation kit included.",
    },
    {
        "category": "screen-protectors",
        "name": "Anti-Glare Matte Protector",
        "brand": "ESR",
        "type": "Matte",
        "material": "Glass",
        "color": "Matte",
        "compatible_with": ["Samsung Galaxy S24"],
        "price": "699",
        "stock": 75,
        "rating": "4.4",
        "review_count": 67,
        "is_new": True,
        "description": "Reduces glare and fingerprints. Great for outdoor use.",
    },
    # Chargers
    {
        "category": "chargers",
        "name": "65W GaN Fast Charger",
        "brand": "Anker",
        "type": "Wall Charger",
        "material": "PC",
        "color": "White",
        "compatible_with": ["Universal"],
        "price": "3499",
        "discount_price": "2999",
        "stock": 32,
        "rating": "4.8",
        "review_count": 156,
        "is_featured": True,
        "description": "Tiny 65W GaN charger with 2 USB-C and 1 USB-A.",
    },
    {
        "category": "chargers",
        "name": "Braided USB-C to Lightning Cable 1.5m",
        "brand": "Baseus",
        "type": "Cable",
        "material": "Nylon Braided",
        "color": "Space Grey",
        "compatible_with": ["iPhone"],
        "price": "899",
        "discount_price": "749",
        "stock": 88,
        "rating": "4.5",
        "review_count": 92,
        "description": "MFi-certified, braided nylon, supports 20W fast charging.",
    },
    # Earbuds
    {
        "category": "earbuds",
        "name": "ANC Wireless Earbuds Pro",
        "brand": "Soundcore",
        "type": "Earbuds",
        "material": "ABS",
        "color": "Onyx Black",
        "compatible_with": ["Universal"],
        "price": "6999",
        "discount_price": "5499",
        "stock": 19,
        "rating": "4.7",
        "review_count": 198,
        "is_featured": True,
        "is_new": True,
        "description": "Active noise cancellation, 36-hour playback, IPX5 water resistance.",
    },
    # Smart Watch
    {
        "category": "smart-watches",
        "name": "Smart Fitness Watch X3",
        "brand": "Noise",
        "type": "Smart Watch",
        "material": "Aluminium",
        "color": "Jet Black",
        "compatible_with": ["Android", "iOS"],
        "price": "4999",
        "discount_price": "3999",
        "stock": 14,
        "rating": "4.4",
        "review_count": 73,
        "is_featured": True,
        "description": '1.96" AMOLED, 100+ sport modes, SpO2, Bluetooth calling.',
    },
    # Power Bank
    {
        "category": "power-banks",
        "name": "20000mAh Fast Charging Power Bank",
        "brand": "Mi",
        "type": "Power Bank",
        "material": "Aluminium",
        "color": "Silver",
        "compatible_with": ["Universal"],
        "price": "2999",
        "discount_price": "2499",
        "stock": 27,
        "rating": "4.6",
        "review_count": 142,
        "description": "20000mAh, 22.5W fast charging, dual USB-C in/out.",
    },
    # Speaker
    {
        "category": "speakers",
        "name": "Bluetooth Party Speaker 30W",
        "brand": "JBL",
        "type": "Speaker",
        "material": "Fabric + ABS",
        "color": "Black",
        "compatible_with": ["Universal"],
        "price": "5499",
        "stock": 9,
        "rating": "4.5",
        "review_count": 38,
        "is_new": True,
        "description": "30W output, IPX7 waterproof, 12hr playback, party-pair mode.",
    },
]


class Command(BaseCommand):
    help = "Seed catalog with sample categories and products."

    def add_arguments(self, parser):
        parser.add_argument(
            "--reset",
            action="store_true",
            help="Delete all existing catalog data before seeding.",
        )

    @transaction.atomic
    def handle(self, *args, **options):
        if options["reset"]:
            self.stdout.write(self.style.WARNING("Deleting existing catalog data…"))
            Product.objects.all().delete()
            Variant.objects.all().delete()
            PhoneModel.objects.all().delete()
            Brand.objects.all().delete()
            Category.objects.all().delete()

        # Categories
        cat_by_slug = {}
        for entry in CATEGORIES:
            cat, created = Category.objects.update_or_create(
                slug=entry["slug"],
                defaults={
                    "name": entry["name"],
                    "description": entry["description"],
                    "icon": entry["icon"],
                    "is_featured": entry["is_featured"],
                    "sort_order": entry["sort_order"],
                },
            )
            cat_by_slug[entry["slug"]] = cat
            self.stdout.write(
                self.style.SUCCESS(("+ " if created else "~ ") + cat.name)
            )

        # Brands — derived from seed data and linked to every category that
        # references them. The form will then surface the right brands once
        # the owner picks a category.
        brand_by_name = {}
        brand_categories: dict[str, set[str]] = {}
        for p in PRODUCTS:
            brand_categories.setdefault(p["brand"], set()).add(p["category"])
        brand_categories.setdefault("Unbranded", set())

        for idx, name in enumerate(sorted(brand_categories.keys())):
            obj, _ = Brand.objects.get_or_create(
                name=name,
                defaults={"sort_order": idx},
            )
            cat_objs = [
                cat_by_slug[slug] for slug in brand_categories[name] if slug in cat_by_slug
            ]
            obj.categories.set(cat_objs)
            brand_by_name[name] = obj

        # Phone models + variants — derived from the legacy compatible_with
        # strings on each seed product. Each brand gets a single ``Default``
        # PhoneModel; every unique (brand, compat_string) under that brand
        # becomes one Variant scoped to that default model. Owners can split
        # the default model into proper ones from /admin/.
        default_model_by_brand: dict[str, PhoneModel] = {}
        variant_by_brand_name: dict[tuple[str, str], Variant] = {}
        for p in PRODUCTS:
            compat = p.get("compatible_with", []) or []
            if not compat:
                continue
            brand_name = p["brand"]
            if brand_name not in default_model_by_brand:
                default_model_by_brand[brand_name], _ = PhoneModel.objects.get_or_create(
                    brand=brand_by_name[brand_name],
                    name="Default",
                )
            default_model = default_model_by_brand[brand_name]
            for compat_name in compat:
                key = (brand_name, compat_name)
                if key in variant_by_brand_name:
                    continue
                variant, _ = Variant.objects.get_or_create(
                    model=default_model,
                    name=compat_name,
                )
                variant_by_brand_name[key] = variant

        # Products
        for p in PRODUCTS:
            cat = cat_by_slug[p["category"]]
            product, _ = Product.objects.update_or_create(
                name=p["name"],
                brand=brand_by_name[p["brand"]],
                defaults={
                    "category": cat,
                    "material": p.get("material", ""),
                    "color": p.get("color", ""),
                    "price": Decimal(p["price"]),
                    "discount_price": (
                        Decimal(p["discount_price"]) if p.get("discount_price") else None
                    ),
                    "stock": p.get("stock", 0),
                    "rating": Decimal(p.get("rating", "0")),
                    "review_count": p.get("review_count", 0),
                    "is_featured": p.get("is_featured", False),
                    "is_new": p.get("is_new", False),
                    "description": p.get("description", ""),
                },
            )
            variants = [
                variant_by_brand_name[(p["brand"], c)]
                for c in (p.get("compatible_with", []) or [])
                if (p["brand"], c) in variant_by_brand_name
            ]
            product.variants.set(variants)
            self.stdout.write(self.style.SUCCESS(f"+ {p['brand']} — {p['name']}"))

        self.stdout.write(self.style.SUCCESS("\nSeeding complete."))
        self.stdout.write(
            self.style.WARNING(
                "\nNote: products were created without images because the Django "
                "ImageField requires an actual file. Upload images via /admin/ or "
                "POST to /api/catalog/products/ with multipart/form-data."
            )
        )

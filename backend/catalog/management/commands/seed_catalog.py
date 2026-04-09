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

from backend.catalog.models import Brand, Category, PhoneModel, Product, ProductType, Variant

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

# Each product defines a "types" list — these become ProductType rows.
# color & stock live on ProductType, not on Product.
PRODUCTS = [
    # ── Mobile Covers ──────────────────────────────────────────────
    {
        "category": "mobile-covers",
        "name": "Carbon Fiber Armor Case",
        "brand": "Spigen",
        "material": "TPU + Polycarbonate",
        "compatible_with": ["iPhone 15 Pro"],
        "price": "2499",
        "discount_price": "1899",
        "rating": "4.7",
        "review_count": 128,
        "hot_sale_live": True,
        "description": "Military-grade drop protection with raised bezels around the camera and screen.",
        "types": [
            {"color": "Matte Black", "stock": 14},
            {"color": "Gunmetal", "stock": 10},
        ],
    },
    {
        "category": "mobile-covers",
        "name": "Liquid Silicone Soft Case",
        "brand": "Apple Style",
        "material": "Silicone",
        "compatible_with": ["Samsung Galaxy S24 Ultra"],
        "price": "1499",
        "discount_price": "1199",
        "rating": "4.5",
        "review_count": 86,
        "hot_sale_live": True,
        "is_new": True,
        "description": "Silky smooth silicone exterior with microfiber lining inside.",
        "types": [
            {"color": "Midnight Blue", "stock": 20},
            {"color": "Lavender", "stock": 12},
            {"color": "Chalk White", "stock": 9},
        ],
    },
    {
        "category": "mobile-covers",
        "name": "Clear Shockproof Case",
        "brand": "ESR",
        "material": "TPU",
        "compatible_with": ["iPhone 14", "iPhone 14 Plus"],
        "price": "999",
        "rating": "4.3",
        "review_count": 54,
        "description": "Anti-yellowing crystal clear case with reinforced air-cushion corners.",
        "types": [
            {"color": "Crystal Clear", "stock": 60},
        ],
    },
    {
        "category": "mobile-covers",
        "name": "MagSafe Leather Wallet Case",
        "brand": "Nillkin",
        "material": "Leather",
        "compatible_with": ["iPhone 15", "iPhone 15 Pro"],
        "price": "3299",
        "discount_price": "2799",
        "rating": "4.8",
        "review_count": 45,
        "hot_sale_live": True,
        "is_new": True,
        "description": "Genuine leather with MagSafe magnets and a slot for two cards.",
        "types": [
            {"color": "Saddle Brown", "stock": 10},
            {"color": "Black", "stock": 8},
        ],
    },
    {
        "category": "mobile-covers",
        "name": "Aramid Fiber Premium Case",
        "brand": "Pitaka",
        "material": "Aramid Fiber",
        "compatible_with": ["iPhone 15 Pro Max"],
        "price": "5999",
        "discount_price": "4999",
        "rating": "4.9",
        "review_count": 31,
        "hot_sale_live": True,
        "is_new": True,
        "description": "Aerospace-grade aramid fiber. Lighter than air, stronger than steel.",
        "types": [
            {"color": "Black/Grey Twill", "stock": 5},
            {"color": "Black/Gold Twill", "stock": 3},
        ],
    },
    # ── Screen Protectors ──────────────────────────────────────────
    {
        "category": "screen-protectors",
        "name": "9H Tempered Glass Protector",
        "brand": "Spigen",
        "material": "Glass",
        "compatible_with": ["iPhone 15"],
        "price": "599",
        "discount_price": "449",
        "rating": "4.6",
        "review_count": 210,
        "hot_sale_live": True,
        "description": "9H hardness with oleophobic coating. Bubble-free installation kit included.",
        "types": [
            {"color": "Clear", "stock": 120},
        ],
    },
    {
        "category": "screen-protectors",
        "name": "Anti-Glare Matte Protector",
        "brand": "ESR",
        "material": "Glass",
        "compatible_with": ["Samsung Galaxy S24"],
        "price": "699",
        "rating": "4.4",
        "review_count": 67,
        "is_new": True,
        "description": "Reduces glare and fingerprints. Great for outdoor use.",
        "types": [
            {"color": "Matte", "stock": 75},
        ],
    },
    # ── Chargers ───────────────────────────────────────────────────
    {
        "category": "chargers",
        "name": "65W GaN Fast Charger",
        "brand": "Anker",
        "material": "PC",
        "compatible_with": ["Universal"],
        "price": "3499",
        "discount_price": "2999",
        "rating": "4.8",
        "review_count": 156,
        "hot_sale_live": True,
        "description": "Tiny 65W GaN charger with 2 USB-C and 1 USB-A.",
        "types": [
            {"color": "White", "stock": 20},
            {"color": "Black", "stock": 12},
        ],
    },
    {
        "category": "chargers",
        "name": "Braided USB-C to Lightning Cable 1.5m",
        "brand": "Baseus",
        "material": "Nylon Braided",
        "compatible_with": ["iPhone"],
        "price": "899",
        "discount_price": "749",
        "rating": "4.5",
        "review_count": 92,
        "description": "MFi-certified, braided nylon, supports 20W fast charging.",
        "types": [
            {"color": "Space Grey", "stock": 50},
            {"color": "Rose Gold", "stock": 38},
        ],
    },
    # ── Earbuds ────────────────────────────────────────────────────
    {
        "category": "earbuds",
        "name": "ANC Wireless Earbuds Pro",
        "brand": "Soundcore",
        "material": "ABS",
        "compatible_with": ["Universal"],
        "price": "6999",
        "discount_price": "5499",
        "rating": "4.7",
        "review_count": 198,
        "hot_sale_live": True,
        "is_new": True,
        "description": "Active noise cancellation, 36-hour playback, IPX5 water resistance.",
        "types": [
            {"color": "Onyx Black", "stock": 10},
            {"color": "Cloud White", "stock": 9},
        ],
    },
    # ── Smart Watch ────────────────────────────────────────────────
    {
        "category": "smart-watches",
        "name": "Smart Fitness Watch X3",
        "brand": "Noise",
        "material": "Aluminium",
        "compatible_with": ["Android", "iOS"],
        "price": "4999",
        "discount_price": "3999",
        "rating": "4.4",
        "review_count": 73,
        "hot_sale_live": True,
        "description": '1.96" AMOLED, 100+ sport modes, SpO2, Bluetooth calling.',
        "types": [
            {"color": "Jet Black", "stock": 8},
            {"color": "Silver Frost", "stock": 6},
        ],
    },
    # ── Power Bank ─────────────────────────────────────────────────
    {
        "category": "power-banks",
        "name": "20000mAh Fast Charging Power Bank",
        "brand": "Mi",
        "material": "Aluminium",
        "compatible_with": ["Universal"],
        "price": "2999",
        "discount_price": "2499",
        "rating": "4.6",
        "review_count": 142,
        "description": "20000mAh, 22.5W fast charging, dual USB-C in/out.",
        "types": [
            {"color": "Silver", "stock": 18},
            {"color": "Black", "stock": 9},
        ],
    },
    # ── Speaker ────────────────────────────────────────────────────
    {
        "category": "speakers",
        "name": "Bluetooth Party Speaker 30W",
        "brand": "JBL",
        "material": "Fabric + ABS",
        "compatible_with": ["Universal"],
        "price": "5499",
        "rating": "4.5",
        "review_count": 38,
        "is_new": True,
        "description": "30W output, IPX7 waterproof, 12hr playback, party-pair mode.",
        "types": [
            {"color": "Black", "stock": 5},
            {"color": "Teal", "stock": 4},
        ],
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
            ProductType.objects.all().delete()
            Product.objects.all().delete()
            Variant.objects.all().delete()
            PhoneModel.objects.all().delete()
            Brand.objects.all().delete()
            Category.objects.all().delete()

        # ── Categories ─────────────────────────────────────────────
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

        # ── Brands ─────────────────────────────────────────────────
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
                cat_by_slug[slug]
                for slug in brand_categories[name]
                if slug in cat_by_slug
            ]
            obj.categories.set(cat_objs)
            brand_by_name[name] = obj

        # ── Phone models + variants ────────────────────────────────
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

        # ── Products + ProductTypes ────────────────────────────────
        for p in PRODUCTS:
            cat = cat_by_slug[p["category"]]
            product, created = Product.objects.update_or_create(
                name=p["name"],
                brand=brand_by_name[p["brand"]],
                defaults={
                    "category": cat,
                    "material": p.get("material", ""),
                    "price": Decimal(p["price"]),
                    "discount_price": (
                        Decimal(p["discount_price"]) if p.get("discount_price") else None
                    ),
                    "rating": Decimal(p.get("rating", "0")),
                    "review_count": p.get("review_count", 0),
                    "hot_sale_live": p.get("hot_sale_live", False),
                    "is_new": p.get("is_new", False),
                    "description": p.get("description", ""),
                },
            )

            # Set compatible variants
            variants = [
                variant_by_brand_name[(p["brand"], c)]
                for c in (p.get("compatible_with", []) or [])
                if (p["brand"], c) in variant_by_brand_name
            ]
            product.variants.set(variants)

            # Create ProductType rows (color + stock)
            for idx, t in enumerate(p.get("types", [])):
                ProductType.objects.update_or_create(
                    product=product,
                    color=t["color"],
                    size=t.get("size", ""),
                    defaults={
                        "stock": t.get("stock", 0),
                        "is_active": True,
                        "sort_order": idx,
                    },
                )

            type_summary = ", ".join(
                f'{t["color"]}({t["stock"]})' for t in p.get("types", [])
            )
            self.stdout.write(
                self.style.SUCCESS(
                    f"{'+ ' if created else '~ '}{p['brand']} — {p['name']}  [{type_summary}]"
                )
            )

        self.stdout.write(self.style.SUCCESS("\nSeeding complete."))
        self.stdout.write(
            self.style.WARNING(
                "\nNote: products were created without images because the Django "
                "ImageField requires an actual file. Upload images via /admin/ or "
                "POST to /api/catalog/products/ with multipart/form-data."
            )
        )

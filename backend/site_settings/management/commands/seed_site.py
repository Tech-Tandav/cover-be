"""Seed the singleton SiteSettings row with the default store content."""
from django.core.management.base import BaseCommand

from backend.site_settings.models import SiteSettings

HERO_STATS = [
    {"value": "500+", "label": "products"},
    {"value": "15+", "label": "brands"},
    {"value": "4.8★", "label": "avg rating"},
]

TRUST_BADGES = [
    {"icon": "Truck", "title": "Same-day delivery", "subtitle": "Within Pokhara"},
    {"icon": "ShieldCheck", "title": "100% Genuine", "subtitle": "Authorized stock"},
    {"icon": "RotateCcw", "title": "7-day returns", "subtitle": "No questions asked"},
    {"icon": "Headset", "title": "Local support", "subtitle": "Call or visit"},
]

SOCIAL_LINKS = [
    {"platform": "facebook", "href": "https://facebook.com/"},
    {"platform": "instagram", "href": "https://instagram.com/"},
]


class Command(BaseCommand):
    help = "Seed singleton site settings with default content."

    def handle(self, *args, **options):
        instance = SiteSettings.load()
        instance.store_name = "E-Store and Accessories"
        instance.store_tagline = "Premium tech accessories in Pokhara"

        instance.hero_eyebrow = "Naya Bazaar, Pokhara · Nepal"
        instance.hero_title_top = "Gear up your"
        instance.hero_title_highlight = "everyday tech."
        instance.hero_subtitle = (
            "Premium covers, screen guards, fast chargers, audio gear and smart "
            "wearables — handpicked for the way you live."
        )
        instance.hero_image_url = (
            "https://images.unsplash.com/photo-1592286927505-1def25115558?w=900&q=80"
        )
        instance.hero_primary_cta_label = "Shop Covers"
        instance.hero_primary_cta_href = "/category/mobile-covers"
        instance.hero_secondary_cta_label = "Browse all"
        instance.hero_secondary_cta_href = "#categories"
        instance.hero_stats = HERO_STATS
        instance.trust_badges = TRUST_BADGES

        instance.address_line1 = "Naya Bazaar, Pokhara-8"
        instance.address_line2 = "Kaski, Gandaki, Nepal"
        instance.phone = "+977 9846-XXXXXX"
        instance.phone_note = "Call or WhatsApp anytime"
        instance.email = "hello@estore.com.np"
        instance.hours = "Sun – Fri · 10:00 AM – 8:00 PM"
        instance.hours_note = "Closed Saturdays"
        instance.map_embed_url = (
            "https://www.openstreetmap.org/export/embed.html?"
            "bbox=83.96%2C28.20%2C84.00%2C28.23&layer=mapnik&marker=28.215%2C83.985"
        )
        instance.map_directions_url = (
            "https://www.google.com/maps/search/?api=1&query=Naya+Bazaar+Pokhara+Nepal"
        )
        instance.social_links = SOCIAL_LINKS

        instance.footer_about = (
            "Your trusted destination in Pokhara for premium mobile covers, "
            "screen protectors, chargers, audio gear and smart wearables. Genuine "
            "products, honest prices, and same-day delivery in-city."
        )
        instance.save()
        self.stdout.write(self.style.SUCCESS("Site settings seeded."))

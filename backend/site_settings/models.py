from django.db import models


class SiteSettings(models.Model):
    """Singleton holding store-wide content shown on the public site."""

    # Branding
    store_name = models.CharField(max_length=120, default="E-Store and Accessories")
    store_tagline = models.CharField(max_length=200, blank=True, default="")

    # Hero
    hero_eyebrow = models.CharField(max_length=120, blank=True, default="")
    hero_title_top = models.CharField(max_length=120, default="Gear up your")
    hero_title_highlight = models.CharField(max_length=120, default="everyday tech.")
    hero_subtitle = models.TextField(
        blank=True,
        default="Premium covers, screen guards, fast chargers, audio gear and smart wearables — handpicked for the way you live.",
    )
    hero_image_url = models.URLField(
        blank=True,
        default="https://images.unsplash.com/photo-1592286927505-1def25115558?w=900&q=80",
    )
    hero_primary_cta_label = models.CharField(max_length=60, default="Shop Covers")
    hero_primary_cta_href = models.CharField(max_length=200, default="/category/mobile-covers")
    hero_secondary_cta_label = models.CharField(max_length=60, default="Browse all")
    hero_secondary_cta_href = models.CharField(max_length=200, default="#categories")

    # Hero stats — list of {value, label}
    hero_stats = models.JSONField(default=list, blank=True)

    # Trust strip — list of {icon, title, subtitle}
    trust_badges = models.JSONField(default=list, blank=True)

    # Store info
    address_line1 = models.CharField(max_length=200, default="Naya Bazaar, Pokhara-8")
    address_line2 = models.CharField(max_length=200, default="Kaski, Gandaki, Nepal")
    phone = models.CharField(max_length=40, default="+977 9846-XXXXXX")
    phone_note = models.CharField(max_length=120, default="Call or WhatsApp anytime")
    email = models.EmailField(default="hello@estore.com.np")
    hours = models.CharField(max_length=120, default="Sun – Fri · 10:00 AM – 8:00 PM")
    hours_note = models.CharField(max_length=120, default="Closed Saturdays")
    map_embed_url = models.URLField(
        blank=True,
        default="https://www.openstreetmap.org/export/embed.html?bbox=83.96%2C28.20%2C84.00%2C28.23&layer=mapnik&marker=28.215%2C83.985",
    )
    map_directions_url = models.URLField(
        blank=True,
        default="https://www.google.com/maps/search/?api=1&query=Naya+Bazaar+Pokhara+Nepal",
    )

    # Socials — list of {platform, href}
    social_links = models.JSONField(default=list, blank=True)

    # Footer
    footer_about = models.TextField(
        blank=True,
        default="Your trusted destination in Pokhara for premium mobile covers, screen protectors, chargers, audio gear and smart wearables. Genuine products, honest prices, and same-day delivery in-city.",
    )

    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Site Settings"
        verbose_name_plural = "Site Settings"

    def __str__(self) -> str:
        return self.store_name

    def save(self, *args, **kwargs):
        # Enforce singleton: always pk=1
        self.pk = 1
        super().save(*args, **kwargs)

    @classmethod
    def load(cls) -> "SiteSettings":
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj

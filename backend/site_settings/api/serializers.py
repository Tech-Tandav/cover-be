from rest_framework import serializers

from backend.site_settings.models import SiteSettings


class SiteSettingsSerializer(serializers.ModelSerializer):
    class Meta:
        model = SiteSettings
        fields = [
            "id",
            "store_name",
            "store_tagline",
            "hero_eyebrow",
            "hero_title_top",
            "hero_title_highlight",
            "hero_subtitle",
            "hero_image_url",
            "hero_primary_cta_label",
            "hero_primary_cta_href",
            "hero_secondary_cta_label",
            "hero_secondary_cta_href",
            "hero_stats",
            "trust_badges",
            "address_line1",
            "address_line2",
            "phone",
            "phone_note",
            "email",
            "hours",
            "hours_note",
            "map_embed_url",
            "map_directions_url",
            "social_links",
            "footer_about",
            "updated_at",
        ]
        read_only_fields = ["id", "updated_at"]

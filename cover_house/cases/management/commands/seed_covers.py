"""
Seed cover taxonomy tables — CaseCategory and CaseColor — with sensible
defaults for a Nepal phone-case shop.

Examples:
    python manage.py seed_covers
    python manage.py seed_covers --reset

Idempotent: re-running adds nothing new.
"""

from django.core.management.base import BaseCommand
from django.db import transaction

from cover_house.cases.models import CaseCategory, CaseColor


CATEGORIES = [
    "Silicone",
    "Clear",
    "Hard Cover",
    "Soft Cover",
    "Rugged",
    "Wallet",
    "Flip",
    "MagSafe",
    "Leather",
    "Hybrid",
]


# (name, hex)
COLORS = [
    ("Black", "#000000"),
    ("White", "#FFFFFF"),
    ("Clear", ""),
    ("Red", "#E53935"),
    ("Blue", "#1E88E5"),
    ("Navy", "#1A237E"),
    ("Green", "#43A047"),
    ("Yellow", "#FDD835"),
    ("Orange", "#FB8C00"),
    ("Pink", "#EC407A"),
    ("Purple", "#8E24AA"),
    ("Gray", "#757575"),
    ("Gold", "#D4AF37"),
    ("Silver", "#C0C0C0"),
    ("Rose Gold", "#B76E79"),
]


class Command(BaseCommand):
    help = "Seed CaseCategory and CaseColor with default values."

    def add_arguments(self, parser):
        parser.add_argument(
            "--reset",
            action="store_true",
            help="Delete all existing categories and colors before seeding.",
        )

    @transaction.atomic
    def handle(self, *args, **options):
        if options["reset"]:
            self.stdout.write(self.style.WARNING("Resetting categories and colors…"))
            CaseCategory.objects.all().delete()
            CaseColor.objects.all().delete()

        cat_created = 0
        for i, name in enumerate(CATEGORIES):
            _, new = CaseCategory.objects.get_or_create(
                name=name, defaults={"sort_order": i}
            )
            cat_created += int(new)

        color_created = 0
        for i, (name, hex_code) in enumerate(COLORS):
            _, new = CaseColor.objects.get_or_create(
                name=name,
                defaults={"hex_code": hex_code, "sort_order": i},
            )
            color_created += int(new)

        self.stdout.write(self.style.SUCCESS(
            f"Done. Categories created: {cat_created}/{len(CATEGORIES)}. "
            f"Colors created: {color_created}/{len(COLORS)}."
        ))

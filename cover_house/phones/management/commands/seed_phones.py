"""
Seed the phone taxonomy from a CSV file.

CSV columns expected:  brand,series,model,variant

Example:
    python manage.py seed_phones                       # default path
    python manage.py seed_phones path/to/file.csv
    python manage.py seed_phones --reset               # wipe taxonomy first

Idempotent: re-running with the same CSV adds nothing new.
"""

import csv
from pathlib import Path

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from cover_house.phones.models import Brand, PhoneModel, PhoneVariant, Series

DEFAULT_CSV = Path(__file__).resolve().parents[4] / "mobile_phones_nepal.csv"


class Command(BaseCommand):
    help = "Seed phone taxonomy (brand → series → model → variant) from a CSV file."

    def add_arguments(self, parser):
        parser.add_argument(
            "csv_path",
            nargs="?",
            default=str(DEFAULT_CSV),
            help=f"Path to CSV file. Default: {DEFAULT_CSV}",
        )
        parser.add_argument(
            "--reset",
            action="store_true",
            help="Delete all existing taxonomy rows before seeding.",
        )

    @transaction.atomic
    def handle(self, *args, **options):
        path = Path(options["csv_path"]).expanduser().resolve()
        if not path.exists():
            raise CommandError(f"CSV not found: {path}")

        if options["reset"]:
            self.stdout.write(self.style.WARNING("Resetting taxonomy tables…"))
            PhoneVariant.objects.all().delete()
            PhoneModel.objects.all().delete()
            Series.objects.all().delete()
            Brand.objects.all().delete()

        created = {"brand": 0, "series": 0, "model": 0, "variant": 0}
        seen = {"brand": 0, "series": 0, "model": 0, "variant": 0}

        with path.open(newline="") as fh:
            reader = csv.DictReader(fh)
            required = {"brand", "series", "model", "variant"}
            if not required.issubset(reader.fieldnames or []):
                raise CommandError(
                    f"CSV must have columns: {sorted(required)} (got {reader.fieldnames})"
                )

            for row in reader:
                row = {k: (v or "").strip() for k, v in row.items()}
                if not all(row[k] for k in required):
                    continue

                brand, b_new = Brand.objects.get_or_create(name=row["brand"])
                created["brand"] += int(b_new); seen["brand"] += 1

                series, s_new = Series.objects.get_or_create(
                    brand=brand, name=row["series"]
                )
                created["series"] += int(s_new); seen["series"] += 1

                model, m_new = PhoneModel.objects.get_or_create(
                    series=series, name=row["model"]
                )
                created["model"] += int(m_new); seen["model"] += 1

                _, v_new = PhoneVariant.objects.get_or_create(
                    phone_model=model, name=row["variant"]
                )
                created["variant"] += int(v_new); seen["variant"] += 1

        self.stdout.write(self.style.SUCCESS(
            f"Done. Rows processed: {seen['variant']}. "
            f"Created — brands: {created['brand']}, series: {created['series']}, "
            f"models: {created['model']}, variants: {created['variant']}."
        ))

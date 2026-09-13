import csv
import re
from decimal import Decimal, InvalidOperation
from pathlib import Path

from django.core.management.base import BaseCommand
from reconciler.models import (
    Organization,
    Location,
    SystemARecord,
    SystemBEntry,
)


def normalize_reference(ref_string: str) -> str:
    """Remove whitespace/symbols and standardize reference IDs."""
    if not ref_string:
        return ""

    return re.sub(r"[^a-zA-Z0-9]", "", str(ref_string)).lower()


def safe_parse_decimal(value_str: str) -> Decimal | None:
    """Parse numeric values safely using Decimal."""
    if value_str is None:
        return None

    value_str = str(value_str).strip()

    if not value_str or value_str.upper() in {"N/A", "NULL", "NONE", "-"}:
        return None

    cleaned = re.sub(r"[^\d.-]", "", value_str)

    if not cleaned:
        return None

    try:
        return Decimal(cleaned)
    except (InvalidOperation, ValueError):
        return None


class Command(BaseCommand):
    help = "Import locations, System A records, and System B entries from CSV files."

    def handle(self, *args, **options):
        project_root = Path(__file__).resolve().parents[4]
        data_dir = project_root / "data"

        locations_file = data_dir / "locations.csv"
        system_a_file = data_dir / "system_a.csv"
        system_b_file = data_dir / "system_b.csv"

        for file_path in [locations_file, system_a_file, system_b_file]:
            if not file_path.exists():
                self.stdout.write(
                    self.style.ERROR(f"File not found: {file_path}")
                )
                return

        self.stdout.write("Starting data import...")

        self.import_locations(locations_file)
        self.import_system_a(system_a_file)
        self.import_system_b(system_b_file)

        self.stdout.write(self.style.SUCCESS("Data import completed successfully."))

    def import_locations(self, file_path):
        count = 0

        with open(file_path, "r", encoding="utf-8-sig", newline="") as file:
            reader = csv.DictReader(file)

            for row in reader:
                location_id = row.get("location_id", "").strip()
                org_id = row.get("org_id", "").strip()
                location_name = row.get("location_name", "").strip()

                if not location_id or not org_id:
                    continue

                organization, _ = Organization.objects.get_or_create(
                    org_id=org_id,
                    defaults={"name": org_id},
                )

                Location.objects.update_or_create(
                    location_id=location_id,
                    defaults={
                        "name": location_name,
                        "organization": organization,
                    },
                )

                count += 1

        self.stdout.write(
            self.style.SUCCESS(
                f"Locations imported: {count}"
            )
        )

    def import_system_a(self, file_path):
        count = 0
        errors = 0

        with open(file_path, "r", encoding="utf-8-sig", newline="") as file:
            reader = csv.DictReader(file)

            for row in reader:
                record_id = row.get("record_id", "").strip()
                location_id_raw = row.get("location_id", "").strip()
                value_raw = row.get("total_value", "").strip()

                if not record_id:
                    continue

                location = Location.objects.filter(
                    location_id=location_id_raw
                ).first()

                organization = location.organization if location else None

                import_errors = []

                if not location:
                    import_errors.append(
                        f"Location not found: {location_id_raw}"
                    )
                    errors += 1

                value_numeric = safe_parse_decimal(value_raw)

                if value_raw and value_numeric is None:
                    import_errors.append(
                        f"Invalid numeric value: {value_raw}"
                    )

                SystemARecord.objects.update_or_create(
                    record_id=record_id,
                    location_id_raw=location_id_raw,
                    defaults={
                        "value_raw": value_raw,
                        "value_numeric": value_numeric,
                        "raw_row": row,
                        "import_errors": import_errors,
                        "organization": organization,
                        "location": location,
                    },
                )

                count += 1

        self.stdout.write(
            self.style.SUCCESS(
                f"System A records imported: {count}"
            )
        )

        if errors:
            self.stdout.write(
                self.style.WARNING(
                    f"System A records with import warnings: {errors}"
                )
            )

    def import_system_b(self, file_path):
        count = 0
        errors = 0

        with open(file_path, "r", encoding="utf-8-sig", newline="") as file:
            reader = csv.DictReader(file)

            for row in reader:
                record_ref_raw = row.get("record_ref", "").strip()
                location_id_raw = row.get("location_id", "").strip()
                value_raw = row.get("value", "").strip()

                if not record_ref_raw:
                    continue

                normalized_ref = normalize_reference(record_ref_raw)

                location = Location.objects.filter(
                    location_id=location_id_raw
                ).first()

                organization = location.organization if location else None

                import_errors = []

                if not location:
                    import_errors.append(
                        f"Location not found: {location_id_raw}"
                    )
                    errors += 1

                value_numeric = safe_parse_decimal(value_raw)

                if value_raw and value_numeric is None:
                    import_errors.append(
                        f"Invalid numeric value: {value_raw}"
                    )

                SystemBEntry.objects.update_or_create(
                    record_ref_raw=record_ref_raw,
                    location_id_raw=location_id_raw,
                    defaults={
                        "record_ref_normalized": normalized_ref,
                        "value_raw": value_raw,
                        "value_numeric": value_numeric,
                        "raw_row": row,
                        "import_errors": import_errors,
                        "organization": organization,
                        "location": location,
                    },
                )

                count += 1

        self.stdout.write(
            self.style.SUCCESS(
                f"System B entries imported: {count}"
            )
        )

        if errors:
            self.stdout.write(
                self.style.WARNING(
                    f"System B entries with import warnings: {errors}"
                )
            )
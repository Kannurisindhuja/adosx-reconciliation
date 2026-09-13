from django.http import JsonResponse
from rest_framework.views import APIView

from .models import SystemARecord, SystemBEntry


def normalize_reference(value):
    """Normalize a record reference for comparison."""
    if value is None:
        return ""

    return "".join(
        char
        for char in str(value).strip().upper()
        if char.isalnum()
    )


def get_cached_discrepancies():
    """Compare System A and System B records."""

    discrepancies = []

    system_a_records = list(SystemARecord.objects.all())
    system_b_entries = list(SystemBEntry.objects.all())

    # Group System B records by normalized reference
    system_b_by_reference = {}

    for entry in system_b_entries:
        reference = normalize_reference(entry.record_ref_raw)

        if reference not in system_b_by_reference:
            system_b_by_reference[reference] = []

        system_b_by_reference[reference].append(entry)

    # Keep track of references existing in System A
    system_a_references = set()

    # Compare System A with System B
    for record in system_a_records:
        reference = normalize_reference(record.record_id)
        system_a_references.add(reference)

        matching_entries = system_b_by_reference.get(reference, [])

        # Missing in System B
        if not matching_entries:
            discrepancies.append({
                "reason": "Missing in System B",
                "record_id": record.record_id,
                "location_id": record.location_id_raw,
                "org_id": (
                    record.organization.org_id
                    if record.organization
                    else None
                ),
                "val_a": (
                    str(record.value_numeric)
                    if record.value_numeric is not None
                    else None
                ),
                "val_b": None,
            })
            continue

        # Duplicate entries in System B
        if len(matching_entries) > 1:
            for entry in matching_entries:
                discrepancies.append({
                    "reason": "Duplicate entry in System B",
                    "record_id": record.record_id,
                    "location_id": record.location_id_raw,
                    "org_id": (
                        record.organization.org_id
                        if record.organization
                        else None
                    ),
                    "val_a": (
                        str(record.value_numeric)
                        if record.value_numeric is not None
                        else None
                    ),
                    "val_b": (
                        str(entry.value_numeric)
                        if entry.value_numeric is not None
                        else None
                    ),
                })

        # Value comparison
        for entry in matching_entries:
            value_a = record.value_numeric
            value_b = entry.value_numeric

            if value_a != value_b:
                discrepancies.append({
                    "reason": "Value mismatch",
                    "record_id": record.record_id,
                    "location_id": record.location_id_raw,
                    "org_id": (
                        record.organization.org_id
                        if record.organization
                        else None
                    ),
                    "val_a": (
                        str(value_a)
                        if value_a is not None
                        else None
                    ),
                    "val_b": (
                        str(value_b)
                        if value_b is not None
                        else None
                    ),
                })

    # Find records that exist only in System B
    for entry in system_b_entries:
        reference = normalize_reference(entry.record_ref_raw)

        if reference not in system_a_references:
            discrepancies.append({
                "reason": "Orphan record in System B",
                "record_id": entry.record_ref_raw,
                "location_id": entry.location_id_raw,
                "org_id": (
                    entry.organization.org_id
                    if entry.organization
                    else None
                ),
                "val_a": None,
                "val_b": (
                    str(entry.value_numeric)
                    if entry.value_numeric is not None
                    else None
                ),
            })

    return discrepancies


class DiscrepancyListView(APIView):

    def get(self, request):
        tenant_org = request.query_params.get("org_id")
        reason_filter = request.query_params.get("reason")

        # Multi-tenant defense
        if not tenant_org:
            return JsonResponse(
                {
                    "error": "org_id query parameter is required"
                },
                status=400,
            )

        # Retrieve discrepancies
        all_discrepancies = get_cached_discrepancies()

        # Strict organization filtering
        tenant_data = [
            discrepancy
            for discrepancy in all_discrepancies
            if discrepancy.get("org_id") == tenant_org
        ]

        # Apply reason filter
        if reason_filter and reason_filter.upper() != "ALL":
            tenant_data = [
                discrepancy
                for discrepancy in tenant_data
                if discrepancy.get("reason") == reason_filter
            ]

        return JsonResponse({
            "count": len(tenant_data),
            "results": tenant_data,
        })

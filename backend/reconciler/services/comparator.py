from collections import defaultdict
from dataclasses import dataclass
from typing import List


@dataclass
class Discrepancy:
    reason: str
    record_id: str
    location_id: str
    org_id: str
    val_a: str | None
    val_b: str | None


def normalize_reference(value):
    """
    Normalize record references so that values like:
    REC-01
     rec-01
    REC-01
    are treated as the same reference.
    """
    return str(value).strip().upper()


def safe_parse_decimal(value):
    """
    Safely convert a value to a number for comparison.
    """
    try:
        return float(value)
    except (ValueError, TypeError):
        return None


def reconcile_records(
    records_a: list,
    records_b: list,
    location_org_map: dict
) -> List[Discrepancy]:

    discrepancies = []

    # 1. Map System B entries by normalized reference key
    b_by_ref = defaultdict(list)

    for b in records_b:
        norm_ref = normalize_reference(b["record_ref"])
        b_by_ref[norm_ref].append(b)

    matched_b_refs = set()

    # 2. Iterate System A records
    for a in records_a:

        norm_id = normalize_reference(a["record_id"])

        org_id = location_org_map.get(
            a.get("location_id"),
            "UNKNOWN"
        )

        b_entries = b_by_ref.get(norm_id, [])

        # Record exists in System A but not System B
        if not b_entries:

            discrepancies.append(
                Discrepancy(
                    reason="MISSING_IN_SYSTEM_B",
                    record_id=a["record_id"],
                    location_id=a.get("location_id"),
                    org_id=org_id,
                    val_a=str(a.get("value")),
                    val_b=None
                )
            )

        # Multiple records with the same reference in System B
        elif len(b_entries) > 1:

            discrepancies.append(
                Discrepancy(
                    reason="DUPLICATE_IN_SYSTEM_B",
                    record_id=a["record_id"],
                    location_id=a.get("location_id"),
                    org_id=org_id,
                    val_a=str(a.get("value")),
                    val_b="; ".join(
                        str(entry.get("value"))
                        for entry in b_entries
                    )
                )
            )

            matched_b_refs.add(norm_id)

        # Exactly one matching record
        else:

            matched_b_refs.add(norm_id)

            val_a_clean = safe_parse_decimal(
                str(a.get("value"))
            )

            val_b_clean = safe_parse_decimal(
                str(b_entries[0].get("value"))
            )

            # Values don't match
            if val_a_clean != val_b_clean:

                discrepancies.append(
                    Discrepancy(
                        reason="VALUE_MISMATCH",
                        record_id=a["record_id"],
                        location_id=a.get("location_id"),
                        org_id=org_id,
                        val_a=str(a.get("value")),
                        val_b=str(
                            b_entries[0].get("value")
                        )
                    )
                )

    # 3. Find orphan entries in System B
    for norm_ref, b_entries in b_by_ref.items():

        if norm_ref not in matched_b_refs and norm_ref != "":

            for orphan in b_entries:

                org_id = location_org_map.get(
                    orphan.get("location_id"),
                    "UNKNOWN"
                )

                discrepancies.append(
                    Discrepancy(
                        reason="ORPHAN_IN_SYSTEM_B",
                        record_id=orphan["record_ref"],
                        location_id=orphan.get("location_id"),
                        org_id=org_id,
                        val_a=None,
                        val_b=str(orphan.get("value"))
                    )
                )

    return discrepancies
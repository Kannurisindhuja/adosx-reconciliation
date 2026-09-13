from django.db import models


class Organization(models.Model):
    org_id = models.CharField(max_length=100, unique=True)
    name = models.CharField(max_length=255, blank=True)

    def __str__(self):
        return self.org_id


class Location(models.Model):
    location_id = models.CharField(max_length=100, unique=True)
    name = models.CharField(max_length=255, blank=True)
    organization = models.ForeignKey(
        Organization,
        on_delete=models.PROTECT,
        related_name="locations",
    )

    def __str__(self):
        return self.location_id


class SystemARecord(models.Model):
    record_id = models.CharField(max_length=255, db_index=True)
    location_id_raw = models.CharField(max_length=255, blank=True)
    value_raw = models.TextField(blank=True)

    # Parsed value. NULL is allowed because source data can be dirty.
    value_numeric = models.DecimalField(
        max_digits=20,
        decimal_places=4,
        null=True,
        blank=True,
    )

    raw_row = models.JSONField(default=dict)
    import_errors = models.JSONField(default=list)

    organization = models.ForeignKey(
        Organization,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="system_a_records",
    )

    location = models.ForeignKey(
        Location,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="system_a_records",
    )

    def __str__(self):
        return self.record_id


class SystemBEntry(models.Model):
    record_ref_raw = models.CharField(max_length=255, blank=True)

    # Canonical reference used for matching.
    record_ref_normalized = models.CharField(
        max_length=255,
        db_index=True,
        blank=True,
    )

    location_id_raw = models.CharField(max_length=255, blank=True)
    value_raw = models.TextField(blank=True)

    value_numeric = models.DecimalField(
        max_digits=20,
        decimal_places=4,
        null=True,
        blank=True,
    )

    raw_row = models.JSONField(default=dict)
    import_errors = models.JSONField(default=list)

    organization = models.ForeignKey(
        Organization,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="system_b_entries",
    )

    location = models.ForeignKey(
        Location,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="system_b_entries",
    )

    def __str__(self):
        return self.record_ref_raw
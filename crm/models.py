"""Domain models for the Epic Events CRM."""

from __future__ import annotations

from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _


class TimestampedModel(models.Model):
    """Abstract model adding creation and update timestamps."""

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class Client(TimestampedModel):
    """A company contact managed by a sales user."""

    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=30, blank=True)
    mobile = models.CharField(max_length=30, blank=True)
    company_name = models.CharField(max_length=150)
    sales_contact = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="sales_clients",
    )

    class Meta:
        ordering = ["last_name", "first_name"]
        indexes = [
            models.Index(fields=["email"]),
            models.Index(fields=["last_name", "first_name"]),
            models.Index(fields=["company_name"]),
        ]

    def __str__(self) -> str:
        return f"{self.full_name} - {self.company_name}"

    @property
    def full_name(self) -> str:
        """Return the client's display name."""
        return f"{self.first_name} {self.last_name}".strip()


class ContractStatus(TimestampedModel):
    """Status used to track the lifecycle of a contract."""

    name = models.CharField(max_length=50, unique=True)
    description = models.TextField(blank=True)
    is_signed = models.BooleanField(default=False)

    class Meta:
        ordering = ["name"]
        verbose_name_plural = "contract statuses"

    def __str__(self) -> str:
        return self.name


class Contract(TimestampedModel):
    """Commercial contract attached to a client."""

    client = models.ForeignKey(Client, on_delete=models.PROTECT, related_name="contracts")
    sales_contact = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="sales_contracts",
    )
    status = models.ForeignKey(
        ContractStatus,
        on_delete=models.PROTECT,
        related_name="contracts",
        null=True,
        blank=True,
    )
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    payment_due = models.DateField(null=True, blank=True)
    signed_at = models.DateField(null=True, blank=True)
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["amount"]),
            models.Index(fields=["payment_due"]),
            models.Index(fields=["signed_at"]),
        ]

    def __str__(self) -> str:
        return f"Contract #{self.pk} - {self.client.full_name}"


class Event(TimestampedModel):
    """Event organized for a signed client contract."""

    class EventStatus(models.TextChoices):
        PLANNED = "planned", _("Planned")
        IN_PROGRESS = "in_progress", _("In progress")
        COMPLETED = "completed", _("Completed")
        CANCELLED = "cancelled", _("Cancelled")

    client = models.ForeignKey(Client, on_delete=models.PROTECT, related_name="events")
    contract = models.ForeignKey(Contract, on_delete=models.PROTECT, related_name="events")
    support_contact = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="support_events",
        null=True,
        blank=True,
    )
    event_status = models.CharField(
        max_length=20,
        choices=EventStatus.choices,
        default=EventStatus.PLANNED,
    )
    event_date = models.DateTimeField()
    attendees = models.PositiveIntegerField(default=0)
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ["event_date"]
        indexes = [
            models.Index(fields=["event_date"]),
            models.Index(fields=["event_status"]),
        ]

    def __str__(self) -> str:
        return f"Event #{self.pk} - {self.client.full_name}"

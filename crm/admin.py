"""Django Admin configuration for CRM models."""

from __future__ import annotations

from django.contrib import admin

from crm.models import Client, Contract, ContractStatus, Event


@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    """Admin interface for clients."""

    list_display = ("full_name", "email", "company_name", "sales_contact", "created_at")
    list_filter = ("sales_contact", "company_name")
    search_fields = ("first_name", "last_name", "email", "company_name")
    autocomplete_fields = ("sales_contact",)


@admin.register(ContractStatus)
class ContractStatusAdmin(admin.ModelAdmin):
    """Admin interface for contract statuses."""

    list_display = ("name", "is_signed", "updated_at")
    search_fields = ("name",)


@admin.register(Contract)
class ContractAdmin(admin.ModelAdmin):
    """Admin interface for contracts."""

    list_display = ("id", "client", "sales_contact", "status", "amount", "payment_due", "signed_at")
    list_filter = ("status", "sales_contact", "payment_due", "signed_at")
    search_fields = (
        "client__first_name",
        "client__last_name",
        "client__email",
        "client__company_name",
    )
    autocomplete_fields = ("client", "sales_contact", "status")


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    """Admin interface for events."""

    list_display = ("id", "client", "contract", "support_contact", "event_status", "event_date")
    list_filter = ("event_status", "support_contact", "event_date")
    search_fields = (
        "client__first_name",
        "client__last_name",
        "client__email",
        "client__company_name",
    )
    autocomplete_fields = ("client", "contract", "support_contact")

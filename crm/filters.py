"""Filter sets used by CRM API endpoints."""

from __future__ import annotations

import django_filters
from django.db.models import Q

from crm.models import Client, Contract, Event


class ClientFilter(django_filters.FilterSet):
    """Search clients with explicit query parameters."""

    name = django_filters.CharFilter(method="filter_name")
    email = django_filters.CharFilter(field_name="email", lookup_expr="icontains")

    class Meta:
        model = Client
        fields = ["name", "email", "company_name", "sales_contact"]

    def filter_name(self, queryset, name, value):
        """Filter clients by first or last name."""
        return queryset.filter(Q(first_name__icontains=value) | Q(last_name__icontains=value))


class ContractFilter(django_filters.FilterSet):
    """Search contracts with client and contract fields."""

    client_name = django_filters.CharFilter(method="filter_client_name")
    client_email = django_filters.CharFilter(field_name="client__email", lookup_expr="icontains")
    contract_date = django_filters.DateFilter(field_name="payment_due")
    contract_date_after = django_filters.DateFilter(field_name="payment_due", lookup_expr="gte")
    contract_date_before = django_filters.DateFilter(field_name="payment_due", lookup_expr="lte")
    amount = django_filters.NumberFilter(field_name="amount")
    amount_min = django_filters.NumberFilter(field_name="amount", lookup_expr="gte")
    amount_max = django_filters.NumberFilter(field_name="amount", lookup_expr="lte")

    class Meta:
        model = Contract
        fields = [
            "client_name",
            "client_email",
            "contract_date",
            "contract_date_after",
            "contract_date_before",
            "amount",
            "amount_min",
            "amount_max",
            "status",
            "sales_contact",
        ]

    def filter_client_name(self, queryset, name, value):
        """Filter contracts by client name."""
        return queryset.filter(
            Q(client__first_name__icontains=value) | Q(client__last_name__icontains=value)
        )


class EventFilter(django_filters.FilterSet):
    """Search events with client and date fields."""

    client_name = django_filters.CharFilter(method="filter_client_name")
    client_email = django_filters.CharFilter(field_name="client__email", lookup_expr="icontains")
    event_date = django_filters.DateFilter(field_name="event_date", lookup_expr="date")
    event_date_after = django_filters.DateFilter(field_name="event_date", lookup_expr="date__gte")
    event_date_before = django_filters.DateFilter(field_name="event_date", lookup_expr="date__lte")

    class Meta:
        model = Event
        fields = [
            "client_name",
            "client_email",
            "event_date",
            "event_date_after",
            "event_date_before",
            "event_status",
            "support_contact",
        ]

    def filter_client_name(self, queryset, name, value):
        """Filter events by client name."""
        return queryset.filter(
            Q(client__first_name__icontains=value) | Q(client__last_name__icontains=value)
        )

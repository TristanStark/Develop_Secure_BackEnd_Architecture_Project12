"""REST API viewsets for Epic Events CRM."""

from __future__ import annotations

from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.exceptions import PermissionDenied
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.viewsets import ModelViewSet

from crm.filters import ClientFilter, ContractFilter, EventFilter
from crm.models import Client, Contract, Event
from crm.permissions import EpicEventsPermission, is_management, is_sales, is_support
from crm.serializers import ClientSerializer, ContractSerializer, EventSerializer

FILTER_BACKENDS = [DjangoFilterBackend, SearchFilter, OrderingFilter]


class ClientViewSet(ModelViewSet):
    """CRUD endpoint for clients with role-filtered querysets."""

    serializer_class = ClientSerializer
    permission_classes = [EpicEventsPermission]
    permission_domain = "clients"
    filterset_class = ClientFilter
    filter_backends = FILTER_BACKENDS
    search_fields = ["first_name", "last_name", "email", "company_name"]
    ordering_fields = ["last_name", "first_name", "email", "company_name", "created_at"]
    ordering = ["last_name", "first_name"]

    def get_queryset(self):
        """Return only clients visible to the current role."""
        user = self.request.user
        queryset = Client.objects.select_related("sales_contact")

        if is_management(user):
            return queryset
        if is_sales(user):
            return queryset.filter(sales_contact=user)
        if is_support(user):
            return queryset.filter(events__support_contact=user).distinct()
        return queryset.none()

    def perform_create(self, serializer: ClientSerializer) -> None:
        """Sales users automatically become the sales contact for new clients."""
        user = self.request.user
        if is_management(user):
            serializer.save()
            return
        serializer.save(sales_contact=user)

    def perform_update(self, serializer: ClientSerializer) -> None:
        """Prevent sales users from reassigning their own clients to another user."""
        user = self.request.user
        if is_management(user):
            serializer.save()
            return
        serializer.save(sales_contact=user)


class ContractViewSet(ModelViewSet):
    """CRUD endpoint for contracts with Sales ownership rules."""

    serializer_class = ContractSerializer
    permission_classes = [EpicEventsPermission]
    permission_domain = "contracts"
    filterset_class = ContractFilter
    filter_backends = FILTER_BACKENDS
    search_fields = [
        "client__first_name",
        "client__last_name",
        "client__email",
        "client__company_name",
    ]
    ordering_fields = ["amount", "payment_due", "signed_at", "created_at"]
    ordering = ["-created_at"]

    def get_queryset(self):
        """Return only contracts visible to the current role."""
        user = self.request.user
        queryset = Contract.objects.select_related("client", "sales_contact", "status")

        if is_management(user):
            return queryset
        if is_sales(user):
            return queryset.filter(client__sales_contact=user)
        return queryset.none()

    def perform_create(self, serializer: ContractSerializer) -> None:
        """Allow sales users to create contracts only for their own clients."""
        user = self.request.user
        client = serializer.validated_data["client"]
        if not is_management(user) and client.sales_contact_id != user.id:
            raise PermissionDenied("You can create contracts only for clients assigned to you.")

        sales_contact = serializer.validated_data.get("sales_contact") or client.sales_contact
        if not is_management(user):
            sales_contact = user
        serializer.save(sales_contact=sales_contact)

    def perform_update(self, serializer: ContractSerializer) -> None:
        """Prevent sales users from moving contracts to clients they do not own."""
        user = self.request.user
        if is_management(user):
            serializer.save()
            return

        client = serializer.validated_data.get("client", serializer.instance.client)
        if client.sales_contact_id != user.id:
            raise PermissionDenied("You can update contracts only for clients assigned to you.")
        serializer.save(sales_contact=user)


class EventViewSet(ModelViewSet):
    """CRUD endpoint for events with Sales creation and Support update rules."""

    serializer_class = EventSerializer
    permission_classes = [EpicEventsPermission]
    permission_domain = "events"
    filterset_class = EventFilter
    filter_backends = FILTER_BACKENDS
    search_fields = [
        "client__first_name",
        "client__last_name",
        "client__email",
        "client__company_name",
        "notes",
    ]
    ordering_fields = ["event_date", "event_status", "created_at"]
    ordering = ["event_date"]

    def get_queryset(self):
        """Return only events visible to the current role."""
        user = self.request.user
        queryset = Event.objects.select_related("client", "contract", "support_contact")

        if is_management(user):
            return queryset
        if is_sales(user):
            return queryset.filter(client__sales_contact=user)
        if is_support(user):
            return queryset.filter(support_contact=user)
        return queryset.none()

    def perform_create(self, serializer: EventSerializer) -> None:
        """Allow sales users to create events only for their own contracts."""
        user = self.request.user
        contract = serializer.validated_data["contract"]
        client = contract.client

        if not is_management(user) and client.sales_contact_id != user.id:
            raise PermissionDenied("You can create events only for contracts assigned to you.")

        serializer.save(client=client)

    def perform_update(self, serializer: EventSerializer) -> None:
        """Support users may update assigned events but cannot reassign ownership."""
        user = self.request.user
        if is_management(user):
            serializer.save()
            return

        event = serializer.instance
        if is_support(user):
            serializer.save(
                client=event.client,
                contract=event.contract,
                support_contact=event.support_contact,
            )
            return

        raise PermissionDenied("Only management or the assigned support user can update an event.")

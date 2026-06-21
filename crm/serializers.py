"""Serializers for the Epic Events REST API."""

from __future__ import annotations

from django.contrib.auth import get_user_model
from rest_framework import serializers

from crm.models import Client, Contract, ContractStatus, Event

User = get_user_model()


class UserSummarySerializer(serializers.ModelSerializer):
    """Small user representation embedded in CRM payloads."""

    class Meta:
        model = User
        fields = ("id", "username", "first_name", "last_name", "email")
        read_only_fields = fields


class ContractStatusSerializer(serializers.ModelSerializer):
    """Serializer for contract statuses."""

    class Meta:
        model = ContractStatus
        fields = ("id", "name", "description", "is_signed", "created_at", "updated_at")
        read_only_fields = ("id", "created_at", "updated_at")


class ClientSerializer(serializers.ModelSerializer):
    """Serializer for client CRUD operations."""

    sales_contact = serializers.PrimaryKeyRelatedField(queryset=User.objects.all(), required=False)
    sales_contact_detail = UserSummarySerializer(source="sales_contact", read_only=True)

    class Meta:
        model = Client
        fields = (
            "id",
            "first_name",
            "last_name",
            "full_name",
            "email",
            "phone",
            "mobile",
            "company_name",
            "sales_contact",
            "sales_contact_detail",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("id", "full_name", "sales_contact_detail", "created_at", "updated_at")


class ContractSerializer(serializers.ModelSerializer):
    """Serializer for contract CRUD operations."""

    sales_contact = serializers.PrimaryKeyRelatedField(queryset=User.objects.all(), required=False)
    client_name = serializers.CharField(source="client.full_name", read_only=True)
    client_email = serializers.EmailField(source="client.email", read_only=True)
    sales_contact_detail = UserSummarySerializer(source="sales_contact", read_only=True)
    status_detail = ContractStatusSerializer(source="status", read_only=True)

    class Meta:
        model = Contract
        fields = (
            "id",
            "client",
            "client_name",
            "client_email",
            "sales_contact",
            "sales_contact_detail",
            "status",
            "status_detail",
            "amount",
            "payment_due",
            "signed_at",
            "notes",
            "created_at",
            "updated_at",
        )
        read_only_fields = (
            "id",
            "client_name",
            "client_email",
            "sales_contact_detail",
            "status_detail",
            "created_at",
            "updated_at",
        )


class EventSerializer(serializers.ModelSerializer):
    """Serializer for event CRUD operations."""

    client = serializers.PrimaryKeyRelatedField(queryset=Client.objects.all(), required=False)
    support_contact = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(), required=False, allow_null=True
    )
    client_name = serializers.CharField(source="client.full_name", read_only=True)
    client_email = serializers.EmailField(source="client.email", read_only=True)
    support_contact_detail = UserSummarySerializer(source="support_contact", read_only=True)

    class Meta:
        model = Event
        fields = (
            "id",
            "client",
            "client_name",
            "client_email",
            "contract",
            "support_contact",
            "support_contact_detail",
            "event_status",
            "event_date",
            "attendees",
            "notes",
            "created_at",
            "updated_at",
        )
        read_only_fields = (
            "id",
            "client_name",
            "client_email",
            "support_contact_detail",
            "created_at",
            "updated_at",
        )

    def validate(self, attrs: dict) -> dict:
        """Keep the duplicated client FK synchronized with the selected contract."""
        contract = attrs.get("contract") or getattr(self.instance, "contract", None)
        client = attrs.get("client") or getattr(self.instance, "client", None)

        if contract is not None and client is None:
            attrs["client"] = contract.client
            return attrs

        if contract is not None and client is not None and contract.client_id != client.id:
            raise serializers.ValidationError(
                {"client": "The event client must be the same client as the selected contract."}
            )

        return attrs

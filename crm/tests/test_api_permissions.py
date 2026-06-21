"""Security-focused API tests for CRM role filtering."""

from __future__ import annotations

from datetime import timedelta

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from rest_framework.test import APIClient

from crm.models import Client, Contract, ContractStatus, Event
from crm.permissions import SALES_GROUP, SUPPORT_GROUP

User = get_user_model()


class ApiPermissionTests(TestCase):
    """Verify that the API never exposes data outside the user's role scope."""

    def setUp(self) -> None:
        """Create a small CRM dataset shared by the permission tests."""
        sales_group = Group.objects.create(name=SALES_GROUP)
        support_group = Group.objects.create(name=SUPPORT_GROUP)

        self.sales_user = User.objects.create_user(username="sales", password="pass")
        self.other_sales_user = User.objects.create_user(username="other-sales", password="pass")
        self.support_user = User.objects.create_user(username="support", password="pass")

        self.sales_user.groups.add(sales_group)
        self.other_sales_user.groups.add(sales_group)
        self.support_user.groups.add(support_group)

        self.client_owned = Client.objects.create(
            first_name="Alice",
            last_name="Martin",
            email="alice@example.com",
            company_name="Alice Corp",
            sales_contact=self.sales_user,
        )
        self.client_hidden = Client.objects.create(
            first_name="Bob",
            last_name="Durand",
            email="bob@example.com",
            company_name="Bob Corp",
            sales_contact=self.other_sales_user,
        )
        self.status = ContractStatus.objects.create(name="Signed", is_signed=True)
        self.contract = Contract.objects.create(
            client=self.client_owned,
            sales_contact=self.sales_user,
            status=self.status,
            amount="1200.00",
        )
        self.event = Event.objects.create(
            client=self.client_owned,
            contract=self.contract,
            support_contact=self.support_user,
            event_date=timezone.now() + timedelta(days=10),
            attendees=50,
        )
        self.api = APIClient()

    def test_anonymous_user_cannot_read_clients(self) -> None:
        """Unauthenticated requests must be rejected."""
        response = self.api.get(reverse("client-list"))

        self.assertIn(response.status_code, {401, 403})

    def test_sales_user_only_sees_assigned_clients(self) -> None:
        """Sales users must not see clients assigned to another sales user."""
        self.api.force_authenticate(self.sales_user)

        response = self.api.get(reverse("client-list"))

        self.assertEqual(response.status_code, 200)
        ids = {item["id"] for item in response.data["results"]}
        self.assertEqual(ids, {self.client_owned.id})

    def test_support_user_sees_only_assigned_events(self) -> None:
        """Support users must see only events assigned to them."""
        self.api.force_authenticate(self.support_user)

        response = self.api.get(reverse("event-list"))

        self.assertEqual(response.status_code, 200)
        ids = {item["id"] for item in response.data["results"]}
        self.assertEqual(ids, {self.event.id})

    def test_support_user_can_update_assigned_event(self) -> None:
        """Support users may update operational fields on their assigned event."""
        self.api.force_authenticate(self.support_user)

        response = self.api.patch(
            reverse("event-detail", kwargs={"pk": self.event.id}),
            {"notes": "Updated by support"},
            format="json",
        )

        self.assertEqual(response.status_code, 200)
        self.event.refresh_from_db()
        self.assertEqual(self.event.notes, "Updated by support")

    def test_support_user_cannot_create_event(self) -> None:
        """Support users can update assigned events but cannot create new events."""
        self.api.force_authenticate(self.support_user)

        response = self.api.post(
            reverse("event-list"),
            {
                "contract": self.contract.id,
                "event_date": (timezone.now() + timedelta(days=20)).isoformat(),
                "attendees": 10,
            },
            format="json",
        )

        self.assertEqual(response.status_code, 403)

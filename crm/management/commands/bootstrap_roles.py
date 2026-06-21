"""Create CRM groups and assign their baseline model permissions."""

from __future__ import annotations

from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from django.core.management.base import BaseCommand

from crm.models import Client, Contract, ContractStatus, Event
from crm.permissions import MANAGEMENT_GROUP, SALES_GROUP, SUPPORT_GROUP


class Command(BaseCommand):
    """Create the Management, Sales, and Support groups used by the API."""

    help = "Create CRM groups and assign their default model permissions."

    def handle(self, *args, **options) -> None:
        """Run the bootstrap process."""
        management_group, _ = Group.objects.get_or_create(name=MANAGEMENT_GROUP)
        sales_group, _ = Group.objects.get_or_create(name=SALES_GROUP)
        support_group, _ = Group.objects.get_or_create(name=SUPPORT_GROUP)

        management_group.permissions.set(self._permissions_for_all_models())
        sales_group.permissions.set(self._sales_permissions())
        support_group.permissions.set(self._support_permissions())

        self.stdout.write(self.style.SUCCESS("CRM groups and permissions were created."))
        self.stdout.write("Reminder: Management users should also have is_staff=True for Django Admin.")

    def _permissions_for_all_models(self) -> list[Permission]:
        """Return all CRM model permissions for management users."""
        models = [Client, ContractStatus, Contract, Event]
        return list(Permission.objects.filter(content_type__in=self._content_types(models)))

    def _sales_permissions(self) -> list[Permission]:
        """Return the model permissions assigned to sales users."""
        wanted = {
            Client: ["add_client", "view_client", "change_client"],
            Contract: ["add_contract", "view_contract", "change_contract"],
            ContractStatus: ["view_contractstatus"],
            Event: ["add_event", "view_event"],
        }
        return self._permissions_from_map(wanted)

    def _support_permissions(self) -> list[Permission]:
        """Return the model permissions assigned to support users."""
        wanted = {
            Client: ["view_client"],
            Contract: ["view_contract"],
            ContractStatus: ["view_contractstatus"],
            Event: ["view_event", "change_event"],
        }
        return self._permissions_from_map(wanted)

    def _permissions_from_map(self, wanted: dict[type, list[str]]) -> list[Permission]:
        """Resolve a model-to-codename map into Permission objects."""
        permissions: list[Permission] = []
        for model, codenames in wanted.items():
            content_type = ContentType.objects.get_for_model(model)
            permissions.extend(
                Permission.objects.filter(content_type=content_type, codename__in=codenames)
            )
        return permissions

    def _content_types(self, models: list[type]) -> list[ContentType]:
        """Return content types for a list of models."""
        return [ContentType.objects.get_for_model(model) for model in models]

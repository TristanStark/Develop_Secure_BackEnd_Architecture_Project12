"""Role-based permissions for the CRM API."""

from __future__ import annotations

from typing import Any

from rest_framework.permissions import SAFE_METHODS, BasePermission


MANAGEMENT_GROUP = "Management Team"
SALES_GROUP = "Sales Team"
SUPPORT_GROUP = "Support Team"


def in_group(user: Any, group_name: str) -> bool:
    """Return whether a Django user belongs to a named group."""
    return bool(user and user.is_authenticated and user.groups.filter(name=group_name).exists())


def is_management(user: Any) -> bool:
    """Return whether a user has management-level CRM access."""
    return bool(user and user.is_authenticated and (user.is_superuser or user.is_staff or in_group(user, MANAGEMENT_GROUP)))


def is_sales(user: Any) -> bool:
    """Return whether a user belongs to the Sales Team group."""
    return in_group(user, SALES_GROUP)


def is_support(user: Any) -> bool:
    """Return whether a user belongs to the Support Team group."""
    return in_group(user, SUPPORT_GROUP)


class EpicEventsPermission(BasePermission):
    """Enforce Management, Sales, and Support permissions on API viewsets."""

    def has_permission(self, request: Any, view: Any) -> bool:
        """Check collection-level access before object filtering is applied."""
        user = request.user
        if not user or not user.is_authenticated:
            return False

        if is_management(user):
            return True

        domain = getattr(view, "permission_domain", "")
        action = getattr(view, "action", "")

        if action in {"list", "retrieve"}:
            if is_sales(user):
                return domain in {"clients", "contracts", "events"}
            if is_support(user):
                return domain in {"clients", "events"}
            return False

        if action == "create":
            return is_sales(user) and domain in {"clients", "contracts", "events"}

        if action in {"update", "partial_update"}:
            if is_sales(user):
                return domain in {"clients", "contracts"}
            if is_support(user):
                return domain == "events"
            return False

        if action == "destroy":
            return False

        return False

    def has_object_permission(self, request: Any, view: Any, obj: Any) -> bool:
        """Check object-level access for the current user and resource."""
        user = request.user
        if is_management(user):
            return True

        domain = getattr(view, "permission_domain", "")

        if domain == "clients":
            return self._can_access_client(request, user, obj)
        if domain == "contracts":
            return self._can_access_contract(request, user, obj)
        if domain == "events":
            return self._can_access_event(request, user, obj)

        return False

    def _can_access_client(self, request: Any, user: Any, client: Any) -> bool:
        """Check access to a client object."""
        if is_sales(user):
            return client.sales_contact_id == user.id

        if is_support(user) and request.method in SAFE_METHODS:
            return client.events.filter(support_contact=user).exists()

        return False

    def _can_access_contract(self, request: Any, user: Any, contract: Any) -> bool:
        """Check access to a contract object."""
        if not is_sales(user):
            return False
        return contract.sales_contact_id == user.id or contract.client.sales_contact_id == user.id

    def _can_access_event(self, request: Any, user: Any, event: Any) -> bool:
        """Check access to an event object."""
        if is_support(user):
            return event.support_contact_id == user.id

        if is_sales(user) and request.method in SAFE_METHODS:
            return event.client.sales_contact_id == user.id

        return False

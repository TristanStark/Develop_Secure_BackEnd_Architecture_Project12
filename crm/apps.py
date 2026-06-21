"""Application configuration for the CRM app."""

from __future__ import annotations

from django.apps import AppConfig


class CrmConfig(AppConfig):
    """Django application configuration for Epic Events CRM."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "crm"
    verbose_name = "Epic Events CRM"

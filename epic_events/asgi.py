"""ASGI configuration for Epic Events CRM."""

from __future__ import annotations

import os

from django.core.asgi import get_asgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "epic_events.settings")

application = get_asgi_application()

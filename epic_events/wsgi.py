"""WSGI configuration for Epic Events CRM."""

from __future__ import annotations

import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "epic_events.settings")

application = get_wsgi_application()

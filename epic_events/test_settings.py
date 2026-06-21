"""Test settings for running the CRM test suite without PostgreSQL."""

from __future__ import annotations

import os

os.environ.setdefault("DJANGO_SECRET_KEY", "test-secret-key")
os.environ.setdefault("DJANGO_DEBUG", "true")
os.environ.setdefault("DJANGO_DB_ENGINE", "django.db.backends.sqlite3")

from epic_events.settings import *  # noqa: F403,E402

DATABASES = {"default": {"ENGINE": "django.db.backends.sqlite3", "NAME": ":memory:"}}
PASSWORD_HASHERS = ["django.contrib.auth.hashers.MD5PasswordHasher"]

# Generated for Epic Events CRM.

from __future__ import annotations

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="ContractStatus",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("name", models.CharField(max_length=50, unique=True)),
                ("description", models.TextField(blank=True)),
                ("is_signed", models.BooleanField(default=False)),
            ],
            options={"ordering": ["name"], "verbose_name_plural": "contract statuses"},
        ),
        migrations.CreateModel(
            name="Client",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("first_name", models.CharField(max_length=100)),
                ("last_name", models.CharField(max_length=100)),
                ("email", models.EmailField(max_length=254, unique=True)),
                ("phone", models.CharField(blank=True, max_length=30)),
                ("mobile", models.CharField(blank=True, max_length=30)),
                ("company_name", models.CharField(max_length=150)),
                (
                    "sales_contact",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="sales_clients",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={"ordering": ["last_name", "first_name"]},
        ),
        migrations.CreateModel(
            name="Contract",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("amount", models.DecimalField(decimal_places=2, max_digits=12)),
                ("payment_due", models.DateField(blank=True, null=True)),
                ("signed_at", models.DateField(blank=True, null=True)),
                ("notes", models.TextField(blank=True)),
                (
                    "client",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="contracts",
                        to="crm.client",
                    ),
                ),
                (
                    "sales_contact",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="sales_contracts",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "status",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="contracts",
                        to="crm.contractstatus",
                    ),
                ),
            ],
            options={"ordering": ["-created_at"]},
        ),
        migrations.CreateModel(
            name="Event",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "event_status",
                    models.CharField(
                        choices=[
                            ("planned", "Planned"),
                            ("in_progress", "In progress"),
                            ("completed", "Completed"),
                            ("cancelled", "Cancelled"),
                        ],
                        default="planned",
                        max_length=20,
                    ),
                ),
                ("event_date", models.DateTimeField()),
                ("attendees", models.PositiveIntegerField(default=0)),
                ("notes", models.TextField(blank=True)),
                (
                    "client",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="events",
                        to="crm.client",
                    ),
                ),
                (
                    "contract",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="events",
                        to="crm.contract",
                    ),
                ),
                (
                    "support_contact",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="support_events",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={"ordering": ["event_date"]},
        ),
        migrations.AddIndex(
            model_name="client",
            index=models.Index(fields=["email"], name="crm_client_email_6861c9_idx"),
        ),
        migrations.AddIndex(
            model_name="client",
            index=models.Index(fields=["last_name", "first_name"], name="crm_client_last_na_6720f3_idx"),
        ),
        migrations.AddIndex(
            model_name="client",
            index=models.Index(fields=["company_name"], name="crm_client_company_790827_idx"),
        ),
        migrations.AddIndex(
            model_name="contract",
            index=models.Index(fields=["amount"], name="crm_contrac_amount_e75f29_idx"),
        ),
        migrations.AddIndex(
            model_name="contract",
            index=models.Index(fields=["payment_due"], name="crm_contrac_payment_1f90d7_idx"),
        ),
        migrations.AddIndex(
            model_name="contract",
            index=models.Index(fields=["signed_at"], name="crm_contrac_signed__009571_idx"),
        ),
        migrations.AddIndex(
            model_name="event",
            index=models.Index(fields=["event_date"], name="crm_event_event_d_e7af47_idx"),
        ),
        migrations.AddIndex(
            model_name="event",
            index=models.Index(fields=["event_status"], name="crm_event_event_s_b8ffef_idx"),
        ),
    ]

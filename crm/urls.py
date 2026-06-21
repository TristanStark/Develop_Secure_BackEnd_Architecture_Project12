"""URL routes for the CRM REST API."""

from __future__ import annotations

from rest_framework.routers import DefaultRouter

from crm.views import ClientViewSet, ContractViewSet, EventViewSet

router = DefaultRouter()
router.register("clients", ClientViewSet, basename="client")
router.register("contracts", ContractViewSet, basename="contract")
router.register("events", EventViewSet, basename="event")

urlpatterns = router.urls

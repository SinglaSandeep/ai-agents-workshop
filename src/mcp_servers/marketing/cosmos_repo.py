"""Read-only Cosmos DB repository for Pepsico marketing campaigns.

You implement this file in **Exercise 04**. Reference solution lives at
``solution/mcp_servers/marketing/cosmos_repo.py``.
"""

from __future__ import annotations

from typing import Any

from src.common.cosmos import get_container
from src.common.settings import get_settings


class MarketingRepository:
    def __init__(self) -> None:
        settings = get_settings()
        self._container = get_container(settings.cosmos_marketing_container)

    def list_active_campaigns(self, limit: int = 20) -> list[dict[str, Any]]:
        """Return up to ``limit`` campaigns whose ``status == 'active'``."""

        # TODO (Exercise 04): SELECT TOP @limit ... WHERE c.status = 'active'.
        raise NotImplementedError

    def list_campaigns_by_brand(self, brand: str, limit: int = 20) -> list[dict[str, Any]]:
        """Return campaigns matching the given brand (case-insensitive)."""

        # TODO (Exercise 04): SELECT TOP @limit ... WHERE LOWER(c.brand) = LOWER(@brand).
        raise NotImplementedError

    def get_campaign(self, campaign_id: str) -> dict[str, Any] | None:
        """Look up a single campaign by id (e.g. ``CMP-2026-001``)."""

        # TODO (Exercise 04): `self._container.read_item(...)`, return None on miss.
        raise NotImplementedError

    def search_campaigns(self, text: str, limit: int = 10) -> list[dict[str, Any]]:
        """Free-text CONTAINS search across campaign name, brand, and summary."""

        # TODO (Exercise 04): SELECT TOP @limit ... WHERE CONTAINS(LOWER(...)).
        raise NotImplementedError

    def campaign_performance(self, campaign_id: str) -> dict[str, Any] | None:
        """Return KPIs (impressions, clicks, CTR, conversions, spend, ROI) for a campaign."""

        # TODO (Exercise 04): call `self.get_campaign(...)` then project the
        # KPI fields into a dict.
        raise NotImplementedError

"""Read-only Cosmos DB repository for Zava marketing campaigns.

Reference solution: ``solution/mcp_servers/marketing/cosmos_repo.py``.
"""

from __future__ import annotations

import logging
import time
from typing import Any

from src.common.cosmos import get_container
from src.common.settings import get_settings

logger = logging.getLogger("zava.mcp.marketing.cosmos")


def _log_query(op, query, params, *, count, elapsed_ms):
    logger.info(
        "cosmos %s rows=%d elapsed_ms=%.1f query=%s params=%s",
        op, count, elapsed_ms, " ".join(query.split()), params or [],
    )


class MarketingRepository:
    def __init__(self) -> None:
        settings = get_settings()
        self._container = get_container(settings.cosmos_marketing_container)

    def list_active_campaigns(self, limit: int = 20) -> list[dict[str, Any]]:
        """Campaigns where ``c.status = 'active'``."""
        # TODO (Exercise 04): SELECT TOP @limit ... WHERE c.status='active'
        raise NotImplementedError

    def list_campaigns_by_category(self, category: str, limit: int = 20) -> list[dict[str, Any]]:
        """Campaigns with ``LOWER(c.category) = LOWER(@cat)``."""
        # TODO (Exercise 04)
        raise NotImplementedError

    def list_campaigns_by_store(self, store_id: str, limit: int = 20) -> list[dict[str, Any]]:
        """Campaigns whose ``c.stores`` array contains ``store_id``.

        Use ``ARRAY_CONTAINS(c.stores, @store_id, false)`` in the WHERE
        clause. This is the primary join hook for cross-domain questions.
        """
        # TODO (Exercise 04)
        raise NotImplementedError

    def get_campaign(self, campaign_id: str) -> dict[str, Any] | None:
        """Read one campaign by id (``ZV-CMP-YYYY-NNN``). Return ``None`` if missing."""
        # TODO (Exercise 04)
        raise NotImplementedError

    def search_campaigns(self, text: str, limit: int = 10) -> list[dict[str, Any]]:
        """Free-text search across campaign name, target_audience, and category."""
        # TODO (Exercise 04)
        raise NotImplementedError

    def campaign_performance(self, campaign_id: str) -> dict[str, Any] | None:
        """KPI snapshot for one campaign: impressions, clicks, CTR, spend, ROI."""
        # TODO (Exercise 04)
        raise NotImplementedError

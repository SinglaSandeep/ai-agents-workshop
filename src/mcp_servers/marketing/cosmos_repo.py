"""Read-only Cosmos DB repository for Zava marketing campaigns."""

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


# Compact projection used by list/search tools. KPI and spend details are
# available through campaign_performance once a campaign id is selected.
_LIST_PROJECTION = (
    "c.id, c.name, c.status, c.category, c.start_date, c.end_date, c.stores, "
    "c.featured_products, c.discount_percent, c.channel, c.kb_brief"
)


class MarketingRepository:
    def __init__(self) -> None:
        settings = get_settings()
        self._container = get_container(settings.cosmos_marketing_container)

    def list_active_campaigns(self, limit: int = 20) -> list[dict[str, Any]]:
        query = f"SELECT TOP @limit {_LIST_PROJECTION} FROM c WHERE c.status = 'active'"
        params = [{"name": "@limit", "value": limit}]
        t0 = time.perf_counter()
        rows = list(self._container.query_items(
            query=query, parameters=params, enable_cross_partition_query=True,
        ))
        _log_query("list_active_campaigns", query, params, count=len(rows),
                   elapsed_ms=(time.perf_counter() - t0) * 1000)
        return rows

    def list_campaigns_by_category(self, category: str, limit: int = 20) -> list[dict[str, Any]]:
        query = (
            f"SELECT TOP @limit {_LIST_PROJECTION} FROM c "
            "WHERE LOWER(c.category) = LOWER(@cat)"
        )
        params = [{"name": "@limit", "value": limit}, {"name": "@cat", "value": category}]
        t0 = time.perf_counter()
        rows = list(self._container.query_items(
            query=query, parameters=params, enable_cross_partition_query=True,
        ))
        _log_query("list_campaigns_by_category", query, params, count=len(rows),
                   elapsed_ms=(time.perf_counter() - t0) * 1000)
        return rows

    def list_campaigns_by_store(self, store_id: str, limit: int = 20) -> list[dict[str, Any]]:
        """Campaigns whose ``stores`` array contains ``store_id``."""
        query = (
            f"SELECT TOP @limit {_LIST_PROJECTION} FROM c "
            "WHERE ARRAY_CONTAINS(c.stores, @store_id, false)"
        )
        params = [{"name": "@limit", "value": limit}, {"name": "@store_id", "value": store_id.lower()}]
        t0 = time.perf_counter()
        rows = list(self._container.query_items(
            query=query, parameters=params, enable_cross_partition_query=True,
        ))
        _log_query("list_campaigns_by_store", query, params, count=len(rows),
                   elapsed_ms=(time.perf_counter() - t0) * 1000)
        return rows

    def get_campaign(self, campaign_id: str) -> dict[str, Any] | None:
        t0 = time.perf_counter()
        try:
            item = self._container.read_item(item=campaign_id, partition_key=campaign_id)
            logger.info("cosmos get_campaign id=%s found=True elapsed_ms=%.1f",
                        campaign_id, (time.perf_counter() - t0) * 1000)
            return self._project_campaign(item)
        except Exception as exc:
            logger.info("cosmos get_campaign id=%s found=False elapsed_ms=%.1f error=%s",
                        campaign_id, (time.perf_counter() - t0) * 1000, exc.__class__.__name__)
            return None

    def search_campaigns(self, text: str, limit: int = 10) -> list[dict[str, Any]]:
        query = (
            f"SELECT TOP @limit {_LIST_PROJECTION} FROM c "
            "WHERE CONTAINS(LOWER(c.name), LOWER(@q)) "
            "   OR CONTAINS(LOWER(c.target_audience), LOWER(@q)) "
            "   OR CONTAINS(LOWER(c.category), LOWER(@q))"
        )
        params = [{"name": "@limit", "value": limit}, {"name": "@q", "value": text}]
        t0 = time.perf_counter()
        rows = list(self._container.query_items(
            query=query, parameters=params, enable_cross_partition_query=True,
        ))
        _log_query("search_campaigns", query, params, count=len(rows),
                   elapsed_ms=(time.perf_counter() - t0) * 1000)
        return rows

    def campaign_performance(self, campaign_id: str) -> dict[str, Any] | None:
        campaign = self.get_campaign(campaign_id)
        if not campaign:
            return None
        impressions = campaign.get("impressions") or 0
        clicks = campaign.get("clicks") or 0
        ctr = (clicks / impressions) if impressions else 0.0
        return {
            "id": campaign["id"],
            "name": campaign.get("name"),
            "status": campaign.get("status"),
            "category": campaign.get("category"),
            "stores": campaign.get("stores"),
            "featured_products": campaign.get("featured_products"),
            "budget_usd": campaign.get("budget_usd"),
            "spend_usd": campaign.get("spend_usd"),
            "impressions": impressions,
            "clicks": clicks,
            "ctr": round(ctr, 4),
            "roi": campaign.get("roi"),
        }

    @staticmethod
    def _project_campaign(campaign: dict[str, Any]) -> dict[str, Any]:
        keys = (
            "id",
            "name",
            "status",
            "category",
            "start_date",
            "end_date",
            "stores",
            "featured_products",
            "discount_percent",
            "channel",
            "target_audience",
            "budget_usd",
            "spend_usd",
            "impressions",
            "clicks",
            "roi",
            "kb_brief",
        )
        return {k: campaign.get(k) for k in keys}

"""Read-only Cosmos DB repository for Pepsico marketing campaigns."""

from __future__ import annotations

import logging
import time
from typing import Any

from src.common.cosmos import get_container
from src.common.settings import get_settings

logger = logging.getLogger("pepsico.mcp.marketing.cosmos")


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
        query = (
            "SELECT TOP @limit c.id, c.campaign_name, c.brand, c.status, c.region, "
            "c.start_date, c.end_date, c.channel, c.target_audience, c.budget_usd "
            "FROM c WHERE c.status = 'active'"
        )
        params = [{"name": "@limit", "value": limit}]
        t0 = time.perf_counter()
        rows = list(self._container.query_items(
            query=query, parameters=params, enable_cross_partition_query=True,
        ))
        _log_query("list_active_campaigns", query, params, count=len(rows),
                   elapsed_ms=(time.perf_counter() - t0) * 1000)
        return rows

    def list_campaigns_by_brand(self, brand: str, limit: int = 20) -> list[dict[str, Any]]:
        query = (
            "SELECT TOP @limit c.id, c.campaign_name, c.brand, c.status, c.region, "
            "c.start_date, c.end_date, c.channel, c.target_audience, c.budget_usd "
            "FROM c WHERE LOWER(c.brand) = LOWER(@brand)"
        )
        params = [{"name": "@limit", "value": limit}, {"name": "@brand", "value": brand}]
        t0 = time.perf_counter()
        rows = list(self._container.query_items(
            query=query, parameters=params, enable_cross_partition_query=True,
        ))
        _log_query("list_campaigns_by_brand", query, params, count=len(rows),
                   elapsed_ms=(time.perf_counter() - t0) * 1000)
        return rows

    def get_campaign(self, campaign_id: str) -> dict[str, Any] | None:
        t0 = time.perf_counter()
        try:
            item = self._container.read_item(item=campaign_id, partition_key=campaign_id)
            logger.info("cosmos get_campaign id=%s found=True elapsed_ms=%.1f",
                        campaign_id, (time.perf_counter() - t0) * 1000)
            return item
        except Exception as exc:
            logger.info("cosmos get_campaign id=%s found=False elapsed_ms=%.1f error=%s",
                        campaign_id, (time.perf_counter() - t0) * 1000, exc.__class__.__name__)
            return None

    def search_campaigns(self, text: str, limit: int = 10) -> list[dict[str, Any]]:
        query = (
            "SELECT TOP @limit c.id, c.campaign_name, c.brand, c.status, c.region, "
            "c.start_date, c.end_date, c.channel, c.target_audience, c.summary, c.budget_usd "
            "FROM c WHERE CONTAINS(LOWER(c.campaign_name), LOWER(@q)) "
            "   OR CONTAINS(LOWER(c.summary), LOWER(@q)) "
            "   OR CONTAINS(LOWER(c.brand), LOWER(@q))"
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
        # No extra log line — `get_campaign` already emits one.
        campaign = self.get_campaign(campaign_id)
        if not campaign:
            return None
        return {
            "id": campaign["id"],
            "campaign_name": campaign.get("campaign_name"),
            "impressions": campaign.get("impressions"),
            "clicks": campaign.get("clicks"),
            "ctr": campaign.get("ctr"),
            "conversions": campaign.get("conversions"),
            "spend_usd": campaign.get("spend_usd"),
            "roi": campaign.get("roi"),
        }

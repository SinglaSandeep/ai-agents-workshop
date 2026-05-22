"""Read-only Cosmos DB repository for Pepsico marketing campaigns."""

from __future__ import annotations

from typing import Any

from src.common.cosmos import get_container
from src.common.settings import get_settings


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
        return list(
            self._container.query_items(
                query=query, parameters=params, enable_cross_partition_query=True
            )
        )

    def list_campaigns_by_brand(self, brand: str, limit: int = 20) -> list[dict[str, Any]]:
        query = (
            "SELECT TOP @limit c.id, c.campaign_name, c.brand, c.status, c.region, "
            "c.start_date, c.end_date, c.channel, c.target_audience, c.budget_usd "
            "FROM c WHERE LOWER(c.brand) = LOWER(@brand)"
        )
        params = [{"name": "@limit", "value": limit}, {"name": "@brand", "value": brand}]
        return list(
            self._container.query_items(
                query=query, parameters=params, enable_cross_partition_query=True
            )
        )

    def get_campaign(self, campaign_id: str) -> dict[str, Any] | None:
        try:
            return self._container.read_item(item=campaign_id, partition_key=campaign_id)
        except Exception:
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
        return list(
            self._container.query_items(
                query=query, parameters=params, enable_cross_partition_query=True
            )
        )

    def campaign_performance(self, campaign_id: str) -> dict[str, Any] | None:
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

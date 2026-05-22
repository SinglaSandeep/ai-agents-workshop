"""Pepsico Marketing MCP server (FastMCP, streamable HTTP transport).

Exposes Cosmos DB-backed tools:
    - list_active_campaigns(limit=20)
    - list_campaigns_by_brand(brand, limit=20)
    - get_campaign(campaign_id)
    - search_campaigns(text, limit=10)
    - campaign_performance(campaign_id)

Run locally:
    uvicorn src.mcp_servers.marketing.server:app --port 8002
Or via CLI:
    pepsico-marketing-mcp
"""

from __future__ import annotations

import os

from fastmcp import FastMCP

from .cosmos_repo import MarketingRepository

mcp = FastMCP(
    name="pepsico-marketing",
    instructions=(
        "Use these tools to look up Pepsico marketing campaigns. "
        "Prefer `search_campaigns` for natural-language questions, "
        "`list_active_campaigns` for what is running today, and "
        "`campaign_performance` for KPI / ROI questions."
    ),
)


def _repo() -> MarketingRepository:
    return MarketingRepository()


@mcp.tool
def list_active_campaigns(limit: int = 20) -> list[dict]:
    """Return marketing campaigns currently marked as `active`."""
    return _repo().list_active_campaigns(limit=limit)


@mcp.tool
def list_campaigns_by_brand(brand: str, limit: int = 20) -> list[dict]:
    """List campaigns by Pepsico brand (e.g. `Gatorade`, `Doritos`, `Pepsi`)."""
    return _repo().list_campaigns_by_brand(brand=brand, limit=limit)


@mcp.tool
def get_campaign(campaign_id: str) -> dict | None:
    """Return the full record for a campaign by id (e.g. `CMP-2026-001`)."""
    return _repo().get_campaign(campaign_id)


@mcp.tool
def search_campaigns(text: str, limit: int = 10) -> list[dict]:
    """Free-text search across campaign name, brand, and summary."""
    return _repo().search_campaigns(text=text, limit=limit)


@mcp.tool
def campaign_performance(campaign_id: str) -> dict | None:
    """Return KPIs (impressions, clicks, CTR, conversions, spend, ROI) for a campaign."""
    return _repo().campaign_performance(campaign_id)


app = mcp.http_app(path="/mcp", transport="streamable-http")


def main() -> None:
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=int(os.getenv("PORT", "8002")))


if __name__ == "__main__":
    main()

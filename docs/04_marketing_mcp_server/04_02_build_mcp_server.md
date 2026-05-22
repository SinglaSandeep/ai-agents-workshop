---
title: '2. Build the FastMCP server'
layout: default
nav_order: 2
parent: 'Exercise 04: Marketing MCP Server'
---

# Task 04.02 — Build the Marketing MCP Server

## Introduction

The Marketing server mirrors the Products one but exposes **five** tools
because marketing teams care about KPIs:

| Tool | Purpose |
| ---- | ------- |
| `list_active_campaigns(limit)` | What is running today |
| `list_campaigns_by_brand(brand, limit)` | Drill into one brand |
| `get_campaign(id)` | Full record for a campaign |
| `search_campaigns(text, limit)` | Free-text questions |
| `campaign_performance(id)` | KPIs only — for ROI questions |

## Success Criteria

* `src/mcp_servers/marketing/cosmos_repo.py` implements all five methods.
* `src/mcp_servers/marketing/server.py` exposes five `@mcp.tool` functions
  on a streamable-HTTP ASGI app at `/mcp`.

## Key Tasks

### 01: Implement `cosmos_repo.py`

Open [src/mcp_servers/marketing/cosmos_repo.py](../../src/mcp_servers/marketing/cosmos_repo.py)
and follow the TODOs.

<details markdown="block">
<summary><strong>Expand this section to view the solution</strong></summary>

```python
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
        return list(self._container.query_items(
            query=query,
            parameters=[{"name": "@limit", "value": limit}],
            enable_cross_partition_query=True,
        ))

    def list_campaigns_by_brand(self, brand: str, limit: int = 20) -> list[dict[str, Any]]:
        query = (
            "SELECT TOP @limit c.id, c.campaign_name, c.brand, c.status, c.region, "
            "c.start_date, c.end_date, c.channel, c.target_audience, c.budget_usd "
            "FROM c WHERE LOWER(c.brand) = LOWER(@brand)"
        )
        params = [{"name": "@limit", "value": limit}, {"name": "@brand", "value": brand}]
        return list(self._container.query_items(
            query=query, parameters=params, enable_cross_partition_query=True,
        ))

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
        return list(self._container.query_items(
            query=query, parameters=params, enable_cross_partition_query=True,
        ))

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
```

</details>

### 02: Implement `server.py`

Open [src/mcp_servers/marketing/server.py](../../src/mcp_servers/marketing/server.py).

<details markdown="block">
<summary><strong>Expand this section to view the solution</strong></summary>

```python
"""Pepsico Marketing MCP server (FastMCP, streamable HTTP transport)."""

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
```

</details>

### 03: Smoke-test locally

```powershell
pepsico-marketing-mcp
# in another terminal
npx @modelcontextprotocol/inspector
```

Connect the Inspector to `http://127.0.0.1:8002/mcp` and confirm all five
tools are listed.

## Next

Continue to [04.03 — Deploy to Azure Container Apps](04_03_deploy_container_app.md).

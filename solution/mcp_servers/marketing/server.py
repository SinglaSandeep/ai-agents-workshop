"""Zava Marketing MCP server (FastMCP, streamable HTTP transport).

Exposes Cosmos DB-backed, task-oriented tools that let an LLM agent answer
questions about Zava's marketing campaigns (categories, stores, featured
SKUs, KPIs, ROI, post-mortems).

Run locally:
    uvicorn src.mcp_servers.marketing.server:app --port 8002
Or via console script:
    zava-marketing-mcp
"""

from __future__ import annotations

import os
from typing import Annotated

from fastmcp import FastMCP
from pydantic import Field

from .cosmos_repo import MarketingRepository

SERVER_INSTRUCTIONS = (
    "Zava Marketing campaigns assistant. Zava is a Pacific Northwest DIY hardware retailer. "
    "Campaigns are scoped by category_id (paint, power-tools, hand-tools, garden, lumber, "
    "electrical, plumbing, hardware) and store_id (seattle, bellevue, tacoma, redmond, kirkland, "
    "spokane, everett, online). Campaign ids look like `ZV-CMP-2026-001`.\n\n"
    "Tool selection guidance:\n"
    "  • `search_campaigns`            → free-text / natural-language ('Spring Paint Sale').\n"
    "  • `list_active_campaigns`       → what's running right now.\n"
    "  • `list_campaigns_by_category`  → user names a category_id.\n"
    "  • `list_campaigns_by_store`     → campaigns running at a specific store_id.\n"
    "  • `campaign_performance`        → KPI / spend / ROI for a specific campaign id.\n"
    "  • `get_campaign`                → full metadata for one campaign id.\n\n"
    "All tools return structured JSON. Currency is USD, dates are ISO-8601 (YYYY-MM-DD), "
    "and CTR is a decimal (0.0172 = 1.72%). When the user asks WHY a campaign performed "
    "the way it did, the answer often lives in the post-mortem KB doc referenced by "
    "`kb_brief` — use the AI Search marketing KB tool to retrieve it. Do NOT invent "
    "campaign ids — only reference ids returned by these tools."
)

mcp = FastMCP(name="zava-marketing", instructions=SERVER_INSTRUCTIONS)


def _repo() -> MarketingRepository:
    return MarketingRepository()


@mcp.tool
def list_active_campaigns(
    limit: Annotated[
        int,
        Field(ge=1, le=100, description="Maximum campaigns to return (1–100). Default 20."),
    ] = 20,
) -> list[dict]:
    """Return campaigns whose status is currently `active`.

    Use when the user asks what is 'running today', 'live', or 'in market'.
    Does NOT include `planned` or `post-mortem` campaigns — use
    `search_campaigns` or `list_campaigns_by_category` for those.
    """
    return _repo().list_active_campaigns(limit=limit)


@mcp.tool
def list_campaigns_by_category(
    category: Annotated[
        str,
        Field(
            min_length=2,
            max_length=64,
            description=(
                "Zava category_id (case-insensitive). One of: paint, power-tools, hand-tools, "
                "garden, lumber, electrical, plumbing, hardware."
            ),
            examples=["paint", "power-tools", "garden"],
        ),
    ],
    limit: Annotated[
        int,
        Field(ge=1, le=100, description="Maximum campaigns to return (1–100). Default 20."),
    ] = 20,
) -> list[dict]:
    """List campaigns for a specific category_id, regardless of status."""
    return _repo().list_campaigns_by_category(category=category, limit=limit)


@mcp.tool
def list_campaigns_by_store(
    store_id: Annotated[
        str,
        Field(
            min_length=2,
            max_length=64,
            description=(
                "Zava store id. One of: seattle, bellevue, tacoma, redmond, kirkland, "
                "spokane, everett, online."
            ),
            examples=["seattle", "bellevue", "online"],
        ),
    ],
    limit: Annotated[
        int,
        Field(ge=1, le=100, description="Maximum campaigns to return (1–100). Default 20."),
    ] = 20,
) -> list[dict]:
    """List campaigns whose ``stores`` array contains ``store_id``.

    This is the primary join hook for cross-domain questions like 'what's
    running at the Seattle store right now?'.
    """
    return _repo().list_campaigns_by_store(store_id=store_id, limit=limit)


@mcp.tool
def get_campaign(
    campaign_id: Annotated[
        str,
        Field(
            description=(
                "Campaign id in the format `ZV-CMP-YYYY-NNN` (e.g. 'ZV-CMP-2026-001'). "
                "Only use ids returned by another tool — do not guess."
            ),
            pattern=r"^ZV-CMP-\d{4}-\d{3,}$",
            examples=["ZV-CMP-2026-001", "ZV-CMP-2025-101"],
        ),
    ],
) -> dict | None:
    """Fetch the full record for one campaign by id.

    Returns `null` if the id is not found — tell the user the campaign does
    not exist rather than fabricating details.
    """
    return _repo().get_campaign(campaign_id)


@mcp.tool
def search_campaigns(
    text: Annotated[
        str,
        Field(
            min_length=2,
            max_length=200,
            description=(
                "Free-text query. Matches campaign name, target_audience, and category "
                "(case-insensitive substring). Use the user's own keywords."
            ),
            examples=["Spring Paint Sale", "Pro Power-Tool Days", "garden weekend"],
        ),
    ],
    limit: Annotated[
        int,
        Field(ge=1, le=50, description="Maximum matches to return (1–50). Default 10."),
    ] = 10,
) -> list[dict]:
    """Free-text search across campaign name, target_audience, and category.

    Preferred tool for natural-language campaign discovery. The result rows
    include a `kb_brief` field — if present, the full creative brief or
    post-mortem is available in the marketing AI Search KB.
    """
    return _repo().search_campaigns(text=text, limit=limit)


@mcp.tool
def campaign_performance(
    campaign_id: Annotated[
        str,
        Field(
            description=(
                "Campaign id in the format `ZV-CMP-YYYY-NNN`. Only use ids returned "
                "by another tool — do not guess."
            ),
            pattern=r"^ZV-CMP-\d{4}-\d{3,}$",
            examples=["ZV-CMP-2026-001"],
        ),
    ],
) -> dict | None:
    """Return KPI metrics for a campaign: impressions, clicks, CTR, spend, ROI, featured products."""
    return _repo().campaign_performance(campaign_id)


# Streamable-HTTP ASGI app — what `uvicorn` and Container Apps will run.
# CORS installed at construction time for browser-based MCP clients.
from starlette.middleware import Middleware  # noqa: E402
from starlette.middleware.cors import CORSMiddleware  # noqa: E402

_cors = Middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["mcp-session-id"],
)

app = mcp.http_app(path="/mcp", transport="streamable-http", middleware=[_cors])


def main() -> None:
    """Entry point for `zava-marketing-mcp` console script."""
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=int(os.getenv("PORT", "8002")))


if __name__ == "__main__":
    main()

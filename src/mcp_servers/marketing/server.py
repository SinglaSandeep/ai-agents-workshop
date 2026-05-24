"""Pepsico Marketing MCP server (FastMCP, streamable HTTP transport).

Exposes Cosmos DB-backed, task-oriented tools that let an LLM agent answer
questions about Pepsico's marketing campaigns (budgets, channels, KPIs, ROI).

Run locally:
    uvicorn src.mcp_servers.marketing.server:app --port 8002
Or via console script (installed by `uv pip install -e .` / `pip install -e .`):
    pepsico-marketing-mcp
Or as a module:
    python -m src.mcp_servers.marketing.server
"""

from __future__ import annotations

import os
from typing import Annotated

from fastmcp import FastMCP
from pydantic import Field

from .cosmos_repo import MarketingRepository

# Server-level instructions guide the LLM at tool-discovery time. Task-oriented
# (per Microsoft MCP best practices) rather than database-oriented.
SERVER_INSTRUCTIONS = (
    "Pepsico Marketing campaigns assistant. Use these tools to answer questions about "
    "Pepsico's marketing programs across brands (Pepsi, Gatorade, Doritos, Mountain Dew, "
    "Lay's, Tropicana, Quaker, Aquafina, etc.) and regions (North America, EMEA, India, "
    "LATAM, Global). Campaign ids look like `CMP-2026-001`.\n\n"
    "Tool selection guidance:\n"
    "  • `search_campaigns`         → free-text / natural-language questions "
    "(\"summer hydration push\", \"IPL sponsorship\").\n"
    "  • `list_active_campaigns`    → \"what is running right now?\".\n"
    "  • `list_campaigns_by_brand`  → user names a specific brand.\n"
    "  • `campaign_performance`     → KPI / ROI / spend / CTR questions for a specific campaign id.\n"
    "  • `get_campaign`             → full metadata for one campaign id.\n\n"
    "All tools return structured JSON. Currency is USD, dates are ISO-8601 (YYYY-MM-DD), "
    "and CTR/ROI are decimal ratios (0.0172 = 1.72%). Do NOT invent campaign ids — only "
    "reference ids returned by these tools."
)

mcp = FastMCP(name="pepsico-marketing", instructions=SERVER_INSTRUCTIONS)


def _repo() -> MarketingRepository:
    return MarketingRepository()


@mcp.tool
def list_active_campaigns(
    limit: Annotated[
        int,
        Field(
            ge=1,
            le=100,
            description="Maximum number of campaigns to return (1–100). Default 20.",
        ),
    ] = 20,
) -> list[dict]:
    """Return marketing campaigns whose status is currently `active`.

    Use this when the user asks what is "running today", "live", or "in market".
    Does NOT include `planned` or `completed` campaigns — use `search_campaigns`
    or `list_campaigns_by_brand` for those.
    """
    return _repo().list_active_campaigns(limit=limit)


@mcp.tool
def list_campaigns_by_brand(
    brand: Annotated[
        str,
        Field(
            min_length=2,
            max_length=64,
            description=(
                "Pepsico brand name (case-insensitive). Examples: 'Gatorade', "
                "'Doritos', 'Pepsi', 'Mountain Dew', 'Lay\u2019s', 'Tropicana', 'Quaker'."
            ),
            examples=["Gatorade", "Doritos", "Pepsi"],
        ),
    ],
    limit: Annotated[
        int,
        Field(
            ge=1,
            le=100,
            description="Maximum number of campaigns to return (1–100). Default 20.",
        ),
    ] = 20,
) -> list[dict]:
    """List campaigns for a specific Pepsico brand, regardless of status."""
    return _repo().list_campaigns_by_brand(brand=brand, limit=limit)


@mcp.tool
def get_campaign(
    campaign_id: Annotated[
        str,
        Field(
            description=(
                "Campaign id in the format `CMP-YYYY-###` (e.g. 'CMP-2026-001'). "
                "Only use ids returned by another tool — do not guess."
            ),
            pattern=r"^CMP-\d{4}-\d{3,}$",
            examples=["CMP-2026-001", "CMP-2026-042"],
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
                "Free-text query. Matches campaign name, brand, and summary "
                "(case-insensitive substring). Use the user's own keywords."
            ),
            examples=["IPL sponsorship", "summer hydration", "Super Bowl"],
        ),
    ],
    limit: Annotated[
        int,
        Field(
            ge=1,
            le=50,
            description="Maximum number of matches to return (1–50). Default 10.",
        ),
    ] = 10,
) -> list[dict]:
    """Free-text search across campaign name, brand, and summary.

    Preferred tool for natural-language campaign discovery.
    """
    return _repo().search_campaigns(text=text, limit=limit)


@mcp.tool
def campaign_performance(
    campaign_id: Annotated[
        str,
        Field(
            description=(
                "Campaign id in the format `CMP-YYYY-###`. Only use ids returned "
                "by another tool — do not guess."
            ),
            pattern=r"^CMP-\d{4}-\d{3,}$",
            examples=["CMP-2026-001"],
        ),
    ],
) -> dict | None:
    """Return KPI metrics for a campaign: impressions, clicks, CTR, conversions, spend, ROI."""
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
    """Entry point for `pepsico-marketing-mcp` console script."""
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=int(os.getenv("PORT", "8002")))


if __name__ == "__main__":
    main()

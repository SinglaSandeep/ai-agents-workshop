"""Zava Sales MCP server (FastMCP, streamable HTTP transport).

Exposes Cosmos DB-backed, task-oriented tools that let an LLM agent surface
sales **insights** (revenue/units/margin trends by store, region, category,
month and product) for the Zava DIY hardware chain. These insights are the
raw signal the Insights-to-Action workflow turns into operational decisions.

Run locally:
    uvicorn src.mcp_servers.sales.server:app --port 8003
Or via console script:
    zava-sales-mcp
"""

from __future__ import annotations

import os
from typing import Annotated

from fastmcp import FastMCP
from pydantic import Field

from .cosmos_repo import SalesRepository

SERVER_INSTRUCTIONS = (
    "Zava Sales insights assistant. Zava is a Pacific Northwest DIY hardware retailer with 7 "
    "stores (seattle, bellevue, tacoma, redmond, kirkland, spokane, everett) plus online, rolled "
    "up into regions (north, south, east, online). Categories: paint, power-tools, hand-tools, "
    "garden, lumber, electrical, plumbing, hardware. Each document is one order line.\n\n"
    "Tool selection guidance:\n"
    "  • `list_dimensions`   → discover valid stores / regions / categories / months first.\n"
    "  • `revenue_summary`   → totals grouped by a dimension (store_id, region, category, month, …).\n"
    "  • `monthly_trend`     → revenue/units/margin per month (optionally filtered) — spot rises/falls.\n"
    "  • `top_products`      → best (or worst, ascending=true) products by revenue/units/margin.\n"
    "  • `sales_for_product` → totals + per-region split for one product_id.\n"
    "  • `get_order`         → one order line by id (ZV-SO-YYYY-NNNNNN).\n\n"
    "All tools return structured JSON. Currency USD, months are 'YYYY-MM'. Product ids follow "
    "ZV-XXX-NNN. Do NOT invent ids or figures — only report values returned by these tools."
)

mcp = FastMCP(name="zava-sales", instructions=SERVER_INSTRUCTIONS)


def _repo() -> SalesRepository:
    return SalesRepository()


@mcp.tool
def list_dimensions() -> dict:
    """List the distinct sales dimensions available (stores, regions, categories, channels, months, segments).

    Call this first when you are unsure which filter values are valid before
    using `revenue_summary`, `monthly_trend` or `top_products`.
    """
    return _repo().list_dimensions()


@mcp.tool
def revenue_summary(
    group_by: Annotated[
        str,
        Field(
            description=(
                "Dimension to aggregate by. One of: store_id, region, category, channel, "
                "customer_segment, month, product_id."
            ),
            examples=["category", "region", "store_id", "month"],
        ),
    ] = "category",
    limit: Annotated[
        int,
        Field(ge=1, le=50, description="Maximum grouped rows to return (1-50). Default 10."),
    ] = 10,
) -> list[dict]:
    """Aggregate total revenue, units, margin and order count grouped by one dimension.

    The primary insight tool. Returns rows sorted by revenue descending::

        { "dimension": "paint", "revenue_usd": 482301.55, "units": 14820,
          "margin_usd": 183274.10, "orders": 2310 }
    """
    return _repo().revenue_summary(group_by=group_by, limit=limit)


@mcp.tool
def monthly_trend(
    category: Annotated[
        str | None,
        Field(description="Optional category_id filter (case-insensitive).", examples=["paint", "garden"]),
    ] = None,
    store_id: Annotated[
        str | None,
        Field(description="Optional store_id filter (case-insensitive).", examples=["seattle", "spokane"]),
    ] = None,
) -> list[dict]:
    """Return revenue/units/margin per month (ascending), optionally filtered by category and/or store.

    Use this to detect a rising or falling trend — the signal that should
    trigger a downstream action (promotion, replenishment, markdown).
    """
    return _repo().monthly_trend(category=category, store_id=store_id)


@mcp.tool
def top_products(
    metric: Annotated[
        str,
        Field(description="Ranking metric: revenue_usd, units, or margin_usd.", examples=["revenue_usd", "units"]),
    ] = "revenue_usd",
    limit: Annotated[int, Field(ge=1, le=25, description="How many products (1-25). Default 5.")] = 5,
    ascending: Annotated[
        bool,
        Field(description="Set true to return the WORST performers (markdown/clearance candidates)."),
    ] = False,
    category: Annotated[
        str | None,
        Field(description="Optional category_id filter (case-insensitive).", examples=["paint", "garden"]),
    ] = None,
) -> list[dict]:
    """Rank products by total revenue, units, or margin. ``ascending=true`` surfaces underperformers.

    Pass ``category`` to rank products within a single category only.
    """
    return _repo().top_products(metric=metric, limit=limit, ascending=ascending, category=category)


@mcp.tool
def sales_for_product(
    product_id: Annotated[
        str,
        Field(
            description="Zava product id (ZV-<CAT>-NNN). Only use ids returned by another tool.",
            pattern=r"^ZV-[A-Z]{3}-\d{3,}$",
            examples=["ZV-PNT-001", "ZV-PWT-003"],
        ),
    ],
) -> dict | None:
    """Total revenue/units/margin for one product plus its per-region split, or null if not found."""
    return _repo().sales_for_product(product_id)


@mcp.tool
def get_order(
    order_id: Annotated[
        str,
        Field(
            description="Sales order-line id (ZV-SO-YYYY-NNNNNN).",
            pattern=r"^ZV-SO-\d{4}-\d{6}$",
            examples=["ZV-SO-2026-000001"],
        ),
    ],
) -> dict | None:
    """Fetch a single order line by id, or null if not found."""
    return _repo().get_order(order_id)


# Streamable-HTTP ASGI app — what Container Apps will run.
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
    """Entry point for the ``zava-sales-mcp`` console script."""
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=int(os.getenv("PORT", "8003")))


if __name__ == "__main__":
    main()

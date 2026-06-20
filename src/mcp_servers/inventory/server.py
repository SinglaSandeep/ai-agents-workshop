"""Zava Inventory MCP server (FastMCP, streamable HTTP transport).

Exposes Cosmos DB-backed, task-oriented tools over **distributor-level
inventory** for the Zava DIY hardware chain. Four distributors stock six
warehouses across the north / south / east / online regions. These tools let an
agent surface stock-health insights (low stock, overstock, weeks of cover,
reorder needs) that the Insights-to-Action workflow converts into operational
moves (replenishment, transfer, markdown).

Run locally:
    uvicorn src.mcp_servers.inventory.server:app --port 8004
Or via console script:
    zava-inventory-mcp
"""

from __future__ import annotations

import os
from typing import Annotated

from fastmcp import FastMCP
from pydantic import Field

from .cosmos_repo import InventoryRepository

SERVER_INSTRUCTIONS = (
    "Zava distributor-inventory assistant. Four distributors supply Zava: "
    "DIST-NW-01 Cascade Supply Co. (north, WH-SEA/WH-BEL), DIST-SW-02 Rainier Wholesale "
    "Partners (south, WH-TAC), DIST-E-03 Inland Northwest Distribution (east, WH-SPO), and "
    "DIST-ON-04 Zava Direct Fulfilment (online, WH-DC1/WH-DC2). Each document is a weekly "
    "snapshot of one product in one warehouse; the newest snapshot per warehouse/product is "
    "flagged is_latest.\n\n"
    "Tool selection guidance:\n"
    "  • `list_distributors`        → discover distributors, their warehouses and regions.\n"
    "  • `stock_status_summary`     → counts of SKUs by status (healthy/low/overstock/stockout).\n"
    "  • `low_stock`                → SKUs at/below reorder point (replenishment candidates).\n"
    "  • `overstock`                → SKUs above max_stock (markdown/transfer candidates).\n"
    "  • `reorder_recommendations`  → low SKUs with a suggested reorder quantity + lead time.\n"
    "  • `inventory_for_product`    → latest cross-warehouse position for one product_id.\n"
    "  • `inventory_trend`          → weekly weeks-of-cover history for a warehouse + product.\n"
    "  • `get_inventory`            → one snapshot document by id.\n\n"
    "All tools return structured JSON. 'weeks_of_cover' = available_units / weekly_demand_units. "
    "Do NOT invent ids or numbers — only report values returned by these tools."
)

mcp = FastMCP(name="zava-inventory", instructions=SERVER_INSTRUCTIONS)


def _repo() -> InventoryRepository:
    return InventoryRepository()


@mcp.tool
def list_distributors() -> list[dict]:
    """List the four distributors with their warehouses and regions."""
    return _repo().list_distributors()


@mcp.tool
def stock_status_summary(
    region: Annotated[
        str | None,
        Field(description="Optional region filter.", examples=["north", "south", "east", "online"]),
    ] = None,
) -> list[dict]:
    """Count latest-snapshot SKUs by stock status, optionally scoped to a region.

    The fastest way to gauge overall inventory health before drilling in.
    """
    return _repo().stock_status_summary(region=region)


@mcp.tool
def low_stock(
    region: Annotated[str | None, Field(description="Optional region filter.")] = None,
    warehouse_id: Annotated[
        str | None,
        Field(description="Optional warehouse filter.", examples=["WH-SEA", "WH-SPO"]),
    ] = None,
    limit: Annotated[int, Field(ge=1, le=100, description="Max rows (1–100). Default 25.")] = 25,
) -> list[dict]:
    """SKUs at or below their reorder point, lowest weeks-of-cover first (replenishment candidates)."""
    return _repo().low_stock(region=region, warehouse_id=warehouse_id, limit=limit)


@mcp.tool
def overstock(
    limit: Annotated[int, Field(ge=1, le=100, description="Max rows (1–100). Default 25.")] = 25,
) -> list[dict]:
    """SKUs flagged overstock (on hand above max_stock), greatest excess first."""
    return _repo().overstock(limit=limit)


@mcp.tool
def reorder_recommendations(
    limit: Annotated[int, Field(ge=1, le=100, description="Max rows (1–100). Default 25.")] = 25,
) -> list[dict]:
    """Low/stockout SKUs with a suggested reorder quantity (to reach max_stock) and lead time."""
    return _repo().reorder_recommendations(limit=limit)


@mcp.tool
def inventory_for_product(
    product_id: Annotated[
        str,
        Field(
            description="Zava product id (ZV-<CAT>-NNN). Only use ids returned by another tool.",
            pattern=r"^ZV-[A-Z]{3}-\d{3,}$",
            examples=["ZV-PNT-001", "ZV-GDN-002"],
        ),
    ],
) -> dict | None:
    """Latest inventory for one product across all warehouses plus aggregate weeks of cover, or null."""
    return _repo().inventory_for_product(product_id)


@mcp.tool
def inventory_trend(
    warehouse_id: Annotated[
        str,
        Field(description="Warehouse id.", examples=["WH-SEA", "WH-DC1"]),
    ],
    product_id: Annotated[
        str,
        Field(
            description="Zava product id (ZV-<CAT>-NNN).",
            pattern=r"^ZV-[A-Z]{3}-\d{3,}$",
            examples=["ZV-PNT-001"],
        ),
    ],
) -> list[dict]:
    """Weekly available-units / weeks-of-cover history for one warehouse + product (oldest first)."""
    return _repo().inventory_trend(warehouse_id=warehouse_id, product_id=product_id)


@mcp.tool
def get_inventory(
    inventory_id: Annotated[
        str,
        Field(description="Inventory snapshot id (ZV-INV-...).", examples=["ZV-INV-WH-SEA-ZV-PNT-001-20260530"]),
    ],
) -> dict | None:
    """Fetch a single inventory snapshot document by id, or null if not found."""
    return _repo().get_inventory(inventory_id)


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
    """Entry point for the ``zava-inventory-mcp`` console script."""
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=int(os.getenv("PORT", "8004")))


if __name__ == "__main__":
    main()

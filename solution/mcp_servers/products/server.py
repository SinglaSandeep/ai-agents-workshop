"""Zava Products MCP server (FastMCP, streamable HTTP transport).

Exposes Cosmos DB-backed, task-oriented tools that let an LLM agent answer
product-catalog and per-store inventory questions for the Zava DIY hardware
chain.

Run locally:
    uvicorn src.mcp_servers.products.server:app --port 8001
Or via CLI:
    zava-products-mcp
"""

from __future__ import annotations

import os
from typing import Annotated

from fastmcp import FastMCP
from pydantic import Field

from .cosmos_repo import ProductsRepository

# Server-level instructions are shown to the LLM during tool discovery. Keep
# them task-oriented rather than describing the underlying database. See:
# https://microsoft.github.io/mcp-azure-security-guide/adoption/development-best-practices/
SERVER_INSTRUCTIONS = (
    "Zava Products catalog & inventory assistant. Zava is a Pacific Northwest DIY hardware "
    "retailer with 7 brick-and-mortar stores (seattle, bellevue, tacoma, redmond, kirkland, "
    "spokane, everett) plus an online fulfillment center (store_id 'online'). Categories: "
    "paint, power-tools, hand-tools, garden, lumber, electrical, plumbing, hardware.\n\n"
    "Tool selection guidance:\n"
    "  • `search_products`    → free-text / natural-language questions ('cordless drill kit').\n"
    "  • `list_products`      → user names a category_id.\n"
    "  • `list_categories`    → enumerate available category ids.\n"
    "  • `get_product`        → fetch one SKU by id (ZV-<CAT>-NNN like ZV-PNT-001).\n"
    "  • `inventory_by_store` → per-store on-hand for one product (returns the inventory_by_store map).\n"
    "  • `low_stock_alerts`   → which products are at or below reorder threshold at a given store.\n\n"
    "All tools return structured JSON. Prices in USD. SKUs follow the pattern ZV-XXX-NNN. "
    "Do NOT invent SKU ids — only reference ids returned by these tools."
)

mcp = FastMCP(name="zava-products", instructions=SERVER_INSTRUCTIONS)


def _repo() -> ProductsRepository:
    # Lazy-construct so importing the module doesn't require Cosmos credentials.
    return ProductsRepository()


@mcp.tool
def list_categories() -> list[str]:
    """List every distinct product category_id in the Zava catalog.

    Use this first when the user asks an open question or before calling
    `list_products` if you're unsure which category strings are valid.

    Returns:
        Sorted list of category id strings, e.g. ``['paint', 'power-tools', 'hardware']``.
        Always non-empty.
    """
    return _repo().list_categories()


@mcp.tool
def list_products(
    category: Annotated[
        str | None,
        Field(
            description=(
                "Optional category_id filter (case-insensitive). Must match one of the values "
                "returned by `list_categories` (e.g. 'paint', 'power-tools'). "
                "Omit or pass null to list across all categories."
            ),
            examples=["paint", "power-tools", "hardware"],
        ),
    ] = None,
    limit: Annotated[
        int,
        Field(ge=1, le=100, description="Maximum products to return (1–100). Default 20."),
    ] = 20,
) -> list[dict]:
    """List Zava products, optionally filtered by category_id.

    Use when the user names a specific category. For natural-language
    questions ('something to paint a fence with'), use `search_products`.

    Each returned record has shape::

        {
          "id": "ZV-PNT-001",
          "name": "Premium Interior Paint - Eggshell White",
          "category": "paint",
          "brand": "Zava Pro",
          "sku": "ZV-PNT-001",
          "unit": "1 gallon",
          "description": "...",
          "price_usd": 32.99,
          "tags": ["paint", "interior", "white"]
        }

    Returns an empty list (never an error) if no products match.
    """
    return _repo().list_products(category=category, limit=limit)


@mcp.tool
def get_product(
    product_id: Annotated[
        str,
        Field(
            description=(
                "Zava product id in the format `ZV-<CAT>-NNN` (e.g. 'ZV-PNT-001'). "
                "Only use ids returned by another tool — do not guess."
            ),
            pattern=r"^ZV-[A-Z]{3}-\d{3,}$",
            examples=["ZV-PNT-001", "ZV-PWT-003", "ZV-HDW-005"],
        ),
    ],
) -> dict | None:
    """Fetch the full record for one product by id.

    Use when the user references a specific SKU or after another tool
    returned an id and you need additional fields (inventory_by_store,
    reorder_threshold, tags, etc.).

    Returns the full record including ``inventory_by_store`` map and
    ``reorder_threshold``, or ``null`` if the id is not found.
    """
    return _repo().get_product(product_id)


@mcp.tool
def search_products(
    text: Annotated[
        str,
        Field(
            min_length=2,
            max_length=200,
            description=(
                "Free-text search query. Matches product name, brand, and description "
                "(case-insensitive substring). Use the user's own keywords."
            ),
            examples=["cordless drill", "interior paint white", "deck screws"],
        ),
    ],
    limit: Annotated[
        int,
        Field(ge=1, le=50, description="Maximum matches to return (1–50). Default 10."),
    ] = 10,
) -> list[dict]:
    """Full-text search across product name, brand, and description.

    Preferred tool for natural-language product discovery. Returns up to
    ``limit`` matches in the same shape as ``list_products``. Empty list
    means no match — suggest the user broaden the query rather than asserting
    the product does not exist.
    """
    return _repo().search_products(text=text, limit=limit)


@mcp.tool
def inventory_by_store(
    product_id: Annotated[
        str,
        Field(
            description="Zava product id (e.g. 'ZV-PNT-001').",
            pattern=r"^ZV-[A-Z]{3}-\d{3,}$",
            examples=["ZV-PNT-001"],
        ),
    ],
) -> dict | None:
    """Return the per-store on-hand inventory map for a single product.

    Use this when the user asks where a product is in stock, or whether a
    specific store has enough on hand. The response looks like::

        {
          "id": "ZV-PNT-001",
          "name": "Premium Interior Paint - Eggshell White",
          "category": "paint",
          "reorder_threshold": 15,
          "inventory_by_store": {
            "seattle": 3, "bellevue": 12, "tacoma": 28, "redmond": 7,
            "kirkland": 33, "spokane": 19, "everett": 14, "online": 220
          }
        }

    Returns ``null`` if the product id is not found.
    """
    return _repo().inventory_by_store(product_id)


@mcp.tool
def low_stock_alerts(
    store_id: Annotated[
        str,
        Field(
            description=(
                "Zava store id. One of: seattle, bellevue, tacoma, redmond, kirkland, "
                "spokane, everett, online."
            ),
            examples=["seattle", "bellevue", "online"],
        ),
    ],
    limit: Annotated[
        int,
        Field(ge=1, le=100, description="Maximum alerts to return (1–100). Default 50."),
    ] = 50,
) -> list[dict]:
    """List products at ``store_id`` whose on-hand stock is at or below their reorder threshold.

    Use this when the user asks about restock priorities, inventory risk for
    a specific store, or wants to find out which SKUs are running low. Sorted
    ascending by on-hand quantity, so the most-urgent rows come first.

    Each result has shape::

        { "id": "ZV-PNT-001", "name": "...", "category": "paint",
          "store_id": "seattle", "on_hand": 3, "reorder_threshold": 15 }
    """
    return _repo().low_stock_alerts(store_id=store_id, limit=limit)


# Streamable-HTTP ASGI app — what Container Apps will run.
# CORS is installed at construction time so browser-based MCP clients
# (e.g. MCP Inspector in Direct mode) can call the server without going
# through the proxy.
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
    """Entry point for the ``zava-products-mcp`` console script."""
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=int(os.getenv("PORT", "8001")))


if __name__ == "__main__":
    main()

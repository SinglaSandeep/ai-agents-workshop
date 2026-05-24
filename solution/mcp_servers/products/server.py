"""Pepsico Products MCP server (FastMCP, streamable HTTP transport).

Exposes Cosmos DB-backed, task-oriented tools that let an LLM agent answer
product-catalog questions for Pepsico's portfolio of beverages and snacks.

Run locally:
    uvicorn src.mcp_servers.products.server:app --port 8001
Or via CLI:
    pepsico-products-mcp
"""

from __future__ import annotations

import os
from typing import Annotated

from fastmcp import FastMCP
from pydantic import Field

from .cosmos_repo import ProductsRepository

# Server-level instructions are shown to the LLM during tool discovery. Keep
# them task-oriented (what the agent can accomplish) rather than describing
# the underlying database. See:
# https://microsoft.github.io/mcp-azure-security-guide/adoption/development-best-practices/
SERVER_INSTRUCTIONS = (
    "Pepsico Products catalog assistant. Use these tools to answer questions "
    "about Pepsico's commercial portfolio of beverages and snacks (Pepsi, Mountain Dew, "
    "Gatorade, Aquafina, Bubly, Lay's, Doritos, Cheetos, Tostitos, Quaker, Tropicana, etc.).\n\n"
    "Tool selection guidance:\n"
    "  • `search_products`  → free-text or fuzzy questions (\"low-calorie sparkling water\", \"spicy chips\").\n"
    "  • `list_products`   → when the user names a category (Beverages, Snacks, Hydration, etc.).\n"
    "  • `list_categories` → when you need to know what categories exist before filtering.\n"
    "  • `get_product`     → when the user supplies an SKU id like `PEP-001` or you already "
    "have an id from a previous tool call and need full details (calories, price, tags).\n\n"
    "All tools return structured JSON (no prose). Numeric fields use USD for price and "
    "kcal for calories. Do NOT invent SKUs — only reference ids returned by these tools."
)

mcp = FastMCP(name="pepsico-products", instructions=SERVER_INSTRUCTIONS)


def _repo() -> ProductsRepository:
    # Lazy-construct so importing the module does not require Cosmos credentials.
    return ProductsRepository()


@mcp.tool
def list_categories() -> list[str]:
    """List every distinct product category in the Pepsico catalog.

    Use this tool first when the user asks an open question like \"what kinds of
    products do you sell?\" or before calling `list_products` if you are unsure
    which category strings are valid.

    Returns:
        Sorted list of category strings, e.g. `[\"Beverages\", \"Hydration\",
        \"Snacks\", \"Cereals\", \"Juices\"]`. Always non-empty.
    """
    return _repo().list_categories()


@mcp.tool
def list_products(
    category: Annotated[
        str | None,
        Field(
            description=(
                "Optional category filter (case-insensitive). Must match one of the values "
                "returned by `list_categories` (e.g. 'Beverages', 'Snacks'). "
                "Omit or pass null to list across all categories."
            ),
            examples=["Beverages", "Snacks"],
        ),
    ] = None,
    limit: Annotated[
        int,
        Field(
            ge=1,
            le=100,
            description="Maximum number of products to return (1–100). Default 20.",
        ),
    ] = 20,
) -> list[dict]:
    """List Pepsico products, optionally filtered by category.

    Use this when the user names a specific product family or category. For
    fuzzy / natural-language questions (\"something low calorie\"), use
    `search_products` instead.

    Each returned record has shape:
        {
          \"id\": \"PEP-001\",
          \"name\": \"Pepsi Cola\",
          \"brand\": \"Pepsi\",
          \"category\": \"Beverages\",
          \"size\": \"12 oz can (12-pack)\",
          \"description\": \"...\",
          \"calories\": 150,
          \"price_usd\": 6.99,
          \"sku\": \"...\",
          \"tags\": [\"cola\", \"caffeinated\"]
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
                "Pepsico product id in the format `PEP-###` (e.g. 'PEP-001'). "
                "Only use ids returned by another tool — do not guess."
            ),
            pattern=r"^PEP-\d{3,}$",
            examples=["PEP-001", "PEP-042"],
        ),
    ],
) -> dict | None:
    """Fetch the full record for one product by id.

    Use this when the user references a specific SKU or after another tool
    returned an id and you need additional fields (calories, price, tags, etc.).

    Returns the same record shape as `list_products`, or `null` if the id is
    not found in the catalog. A `null` return is not an error — inform the
    user the SKU does not exist and ask for clarification.
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
                "Free-text search query. Matches against product name, brand, "
                "and description (case-insensitive, substring match). Use the user's "
                "own keywords; do not over-paraphrase."
            ),
            examples=["sparkling water", "spicy chips", "electrolyte"],
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
    """Full-text search across product name, brand, and description.

    This is the **preferred tool** for natural-language product discovery.
    Examples of good queries: \"zero sugar cola\", \"baked snacks\", \"Gatorade lemon\".

    Returns up to `limit` matching products in the same record shape as
    `list_products`. Returns an empty list if nothing matches — in that case,
    suggest the user broaden the query rather than asserting the product does
    not exist.
    """
    return _repo().search_products(text=text, limit=limit)


# Streamable-HTTP ASGI app — what Container Apps will run.
app = mcp.http_app(path="/mcp", transport="streamable-http")


def main() -> None:
    """Entry point for `pepsico-products-mcp` console script."""
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=int(os.getenv("PORT", "8001")))


if __name__ == "__main__":
    main()

"""Pepsico Products MCP server (FastMCP, streamable HTTP transport).

Exposes Cosmos DB-backed tools:
    - list_categories()
    - list_products(category=None, limit=20)
    - get_product(product_id)
    - search_products(text, limit=10)

Run locally:
    uvicorn src.mcp_servers.products.server:app --port 8001
Or via CLI:
    pepsico-products-mcp
"""

from __future__ import annotations

import os

from fastmcp import FastMCP

from .cosmos_repo import ProductsRepository

mcp = FastMCP(
    name="pepsico-products",
    instructions=(
        "Use these tools to look up Pepsico products in the catalog. "
        "Prefer `search_products` for free-text questions and `list_products` "
        "when the user names a specific category (Beverages, Snacks, etc.)."
    ),
)


def _repo() -> ProductsRepository:
    # Lazy-construct so importing the module does not require Cosmos credentials.
    return ProductsRepository()


@mcp.tool
def list_categories() -> list[str]:
    """List all distinct product categories available in the Pepsico catalog."""
    return _repo().list_categories()


@mcp.tool
def list_products(category: str | None = None, limit: int = 20) -> list[dict]:
    """List Pepsico products, optionally filtered by category (case-insensitive)."""
    return _repo().list_products(category=category, limit=limit)


@mcp.tool
def get_product(product_id: str) -> dict | None:
    """Return the full record for one product by id (e.g. `PEP-001`)."""
    return _repo().get_product(product_id)


@mcp.tool
def search_products(text: str, limit: int = 10) -> list[dict]:
    """Full-text search across product name, brand, and description."""
    return _repo().search_products(text=text, limit=limit)


# Streamable-HTTP ASGI app — what Container Apps will run.
app = mcp.http_app(path="/mcp", transport="streamable-http")


def main() -> None:
    """Entry point for `pepsico-products-mcp` console script."""
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=int(os.getenv("PORT", "8001")))


if __name__ == "__main__":
    main()

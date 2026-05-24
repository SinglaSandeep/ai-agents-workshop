"""Zava Products MCP server (FastMCP, streamable HTTP transport)."""

from __future__ import annotations

import os

from fastmcp import FastMCP

from .cosmos_repo import ProductsRepository

mcp = FastMCP(
    name="Zava-products",
    instructions=(
        "Use these tools to look up Zava products in the catalog. "
        "Prefer `search_products` for free-text questions and `list_products` "
        "when the user names a specific category (Beverages, Snacks, etc.)."
    ),
)


def _repo() -> ProductsRepository:
    return ProductsRepository()


@mcp.tool
def list_categories() -> list[str]:
    """List all distinct product categories available in the Zava catalog."""
    return _repo().list_categories()


@mcp.tool
def list_products(category: str | None = None, limit: int = 20) -> list[dict]:
    """List Zava products, optionally filtered by category (case-insensitive)."""
    return _repo().list_products(category=category, limit=limit)


@mcp.tool
def get_product(product_id: str) -> dict | None:
    """Return the full record for one product by id (e.g. `ZV-PNT-001`)."""
    return _repo().get_product(product_id)


@mcp.tool
def search_products(text: str, limit: int = 10) -> list[dict]:
    """Full-text search across product name, brand, and description."""
    return _repo().search_products(text=text, limit=limit)


app = mcp.http_app(path="/mcp", transport="streamable-http")


def main() -> None:
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=int(os.getenv("PORT", "8001")))


if __name__ == "__main__":
    main()

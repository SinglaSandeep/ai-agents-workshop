"""Zava **Products** MCP server (FastMCP, streamable HTTP transport).

You build this file out in **Exercise 02**. When complete, it will expose
six Cosmos DB-backed MCP tools that the Products Foundry agent (Exercise 03)
will call:

* ``list_categories()``
* ``list_products(category=None, limit=20)``
* ``get_product(product_id)``                  — id pattern ``ZV-<CAT>-NNN``
* ``search_products(text, limit=10)``
* ``inventory_by_store(product_id)``           — per-store on-hand map
* ``low_stock_alerts(store_id, limit=50)``     — reorder candidates by store

Run locally (after you complete Exercise 02):

    uvicorn src.mcp_servers.products.server:app --port 8001

Reference solution: ``solution/mcp_servers/products/server.py``.
"""

from __future__ import annotations

import os

# TODO (Exercise 02 / Task 02.02): import FastMCP and your ProductsRepository.
#   from fastmcp import FastMCP
#   from .cosmos_repo import ProductsRepository


# TODO (Exercise 02 / Task 02.02): instantiate the FastMCP app with a name
# and rich, task-oriented `instructions` text. The instructions are read by
# the calling LLM at tool-discovery time and help it pick the right tool.
# Follow Microsoft's MCP development best practices:
# https://microsoft.github.io/mcp-azure-security-guide/adoption/development-best-practices/
#
# Good instructions explain (1) what the server does, (2) the entities in
# scope (Zava categories, store ids, ZV-XXX-NNN SKU pattern), (3) tool-
# selection guidance, and (4) data conventions (USD, store_id values).
# Example:
#
#   mcp = FastMCP(
#       name="zava-products",
#       instructions=(
#           "Zava Products catalog & inventory assistant. Use these tools "
#           "to answer questions about Zava DIY products and per-store "
#           "inventory.\n\n"
#           "Tool selection:\n"
#           "  • `search_products`    → free-text questions\n"
#           "  • `list_products`      → user names a category_id\n"
#           "  • `list_categories`    → enumerate available categories\n"
#           "  • `get_product`        → fetch one SKU by id (ZV-XXX-NNN)\n"
#           "  • `inventory_by_store` → per-store on-hand for a product\n"
#           "  • `low_stock_alerts`   → reorder candidates by store_id\n\n"
#           "Prices in USD. Categories: paint, power-tools, hand-tools, "
#           "garden, lumber, electrical, plumbing, hardware. Stores: "
#           "seattle, bellevue, tacoma, redmond, kirkland, spokane, "
#           "everett, online. Do not invent SKU ids."
#       ),
#   )


# TODO (Exercise 02 / Task 02.02): for each of the six tools, write a
# Python function and decorate it with `@mcp.tool`. The docstring becomes
# the tool description the LLM sees, and the type hints become the JSON
# schema. A good tool description tells the LLM (1) what it does in one
# sentence, (2) WHEN to pick it over similar tools, (3) the return shape,
# and (4) what `null` / empty results mean.
#
# Add parameter constraints/descriptions via `Annotated[..., Field(...)]`
# so the LLM sees richer JSON Schema (regex patterns, min/max, examples):
#
#   from typing import Annotated
#   from pydantic import Field
#
#   def _repo() -> "ProductsRepository":
#       return ProductsRepository()
#
#   @mcp.tool
#   def list_categories() -> list[str]:
#       """List every distinct product category_id in the catalog."""
#       return _repo().list_categories()
#
#   @mcp.tool
#   def get_product(
#       product_id: Annotated[
#           str,
#           Field(pattern=r"^ZV-[A-Z]{3}-\d{3,}$", examples=["ZV-PNT-001"],
#                 description="Zava SKU id like 'ZV-PNT-001'. Do not guess."),
#       ],
#   ) -> dict | None:
#       """Fetch one product by id. Returns null if the SKU does not exist."""
#       return _repo().get_product(product_id)


# TODO (Exercise 02 / Task 02.02): expose the FastMCP app as an ASGI app over
# the streamable-HTTP transport. The Foundry MCPTool expects this transport.
#
#   app = mcp.http_app(path="/mcp", transport="streamable-http")
app = None  # replaced in Exercise 02


def main() -> None:
    """Entry point for the ``zava-products-mcp`` console script."""

    import uvicorn

    if app is None:
        raise RuntimeError(
            "The Products MCP server is not implemented yet — complete "
            "Exercise 02 to build it."
        )
    uvicorn.run(app, host="0.0.0.0", port=int(os.getenv("PORT", "8001")))


if __name__ == "__main__":
    main()

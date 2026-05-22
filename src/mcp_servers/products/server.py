"""Pepsico **Products** MCP server (FastMCP, streamable HTTP transport).

You build this file out in **Exercise 02**. When complete, it will expose
four Cosmos DB-backed MCP tools that the Products Foundry agent (Exercise 03)
will call:

* ``list_categories()``
* ``list_products(category=None, limit=20)``
* ``get_product(product_id)``
* ``search_products(text, limit=10)``

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
# and clear `instructions` text. The instructions are read by the calling
# LLM and help it pick the right tool.
#
#   mcp = FastMCP(
#       name="pepsico-products",
#       instructions=(
#           "Use these tools to look up Pepsico products in the catalog. "
#           "Prefer `search_products` for free-text questions and `list_products` "
#           "when the user names a specific category (Beverages, Snacks, etc.)."
#       ),
#   )


# TODO (Exercise 02 / Task 02.02): for each of the four tools, write a
# Python function and decorate it with `@mcp.tool`. The docstring becomes
# the tool description the LLM sees, and the type hints become the JSON
# schema. Example shape:
#
#   def _repo() -> "ProductsRepository":
#       return ProductsRepository()
#
#   @mcp.tool
#   def list_categories() -> list[str]:
#       """List all distinct product categories available in the Pepsico catalog."""
#       return _repo().list_categories()


# TODO (Exercise 02 / Task 02.02): expose the FastMCP app as an ASGI app over
# the streamable-HTTP transport. The Foundry MCPTool expects this transport.
#
#   app = mcp.http_app(path="/mcp", transport="streamable-http")
app = None  # replaced in Exercise 02


def main() -> None:
    """Entry point for the ``pepsico-products-mcp`` console script."""

    import uvicorn

    if app is None:
        raise RuntimeError(
            "The Products MCP server is not implemented yet — complete "
            "Exercise 02 to build it."
        )
    uvicorn.run(app, host="0.0.0.0", port=int(os.getenv("PORT", "8001")))


if __name__ == "__main__":
    main()

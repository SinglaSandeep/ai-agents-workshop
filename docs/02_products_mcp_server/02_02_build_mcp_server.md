---
title: '2. Build the FastMCP server'
layout: default
nav_order: 2
parent: 'Exercise 02: Products MCP Server'
---

# Task 02.02 — Build the Products MCP Server

## Introduction

You will now fill in two starter files:

* `src/mcp_servers/products/cosmos_repo.py` — a thin read-only repository over
  the Cosmos `products` container.
* `src/mcp_servers/products/server.py` — the FastMCP app that exposes four
  tools.

The reference implementations live under
`solution/mcp_servers/products/`. Try writing them yourself first — peek only
if you get stuck.

## Success Criteria

* `cosmos_repo.py` implements `list_categories`, `list_products`,
  `get_product`, and `search_products`.
* `server.py` registers four `@mcp.tool` functions and exposes a streamable
  HTTP ASGI app at `/mcp`.
* `python -c "from src.mcp_servers.products import server; print(server.app)"`
  prints an ASGI app object, not `None`.

## Key Tasks

### 01: Implement `cosmos_repo.py`

Open [src/mcp_servers/products/cosmos_repo.py](../../src/mcp_servers/products/cosmos_repo.py).
The skeleton already imports `get_container` from `src.common.cosmos` and
selects the products container in `__init__`. You just need to fill in each
query method.

<details markdown="block">
<summary><strong>Expand this section to view the solution</strong></summary>

```python
"""Read-only Cosmos DB repository for the Pepsico products catalog."""

from __future__ import annotations

from typing import Any

from src.common.cosmos import get_container
from src.common.settings import get_settings


class ProductsRepository:
    def __init__(self) -> None:
        settings = get_settings()
        self._container = get_container(settings.cosmos_products_container)

    def list_categories(self) -> list[str]:
        query = "SELECT DISTINCT VALUE c.category FROM c"
        return [
            c
            for c in self._container.query_items(
                query=query, enable_cross_partition_query=True
            )
        ]

    def list_products(self, category: str | None = None, limit: int = 20) -> list[dict[str, Any]]:
        if category:
            query = (
                "SELECT TOP @limit c.id, c.name, c.category, c.brand, c.size, "
                "c.description, c.calories, c.price_usd "
                "FROM c WHERE LOWER(c.category) = LOWER(@cat)"
            )
            params = [
                {"name": "@limit", "value": limit},
                {"name": "@cat", "value": category},
            ]
        else:
            query = (
                "SELECT TOP @limit c.id, c.name, c.category, c.brand, c.size, "
                "c.description, c.calories, c.price_usd FROM c"
            )
            params = [{"name": "@limit", "value": limit}]
        return list(
            self._container.query_items(
                query=query,
                parameters=params,
                enable_cross_partition_query=True,
            )
        )

    def get_product(self, product_id: str) -> dict[str, Any] | None:
        try:
            return self._container.read_item(item=product_id, partition_key=product_id)
        except Exception:
            return None

    def search_products(self, text: str, limit: int = 10) -> list[dict[str, Any]]:
        query = (
            "SELECT TOP @limit c.id, c.name, c.category, c.brand, c.size, "
            "c.description, c.calories, c.price_usd FROM c "
            "WHERE CONTAINS(LOWER(c.name), LOWER(@q)) "
            "   OR CONTAINS(LOWER(c.description), LOWER(@q)) "
            "   OR CONTAINS(LOWER(c.brand), LOWER(@q))"
        )
        params = [
            {"name": "@limit", "value": limit},
            {"name": "@q", "value": text},
        ]
        return list(
            self._container.query_items(
                query=query,
                parameters=params,
                enable_cross_partition_query=True,
            )
        )
```

Note: we keep the surface **read-only** and return plain `dict`s so the MCP
server can JSON-serialise the response straight back to the LLM.

</details>

### 02: Implement `server.py`

Open [src/mcp_servers/products/server.py](../../src/mcp_servers/products/server.py).
Follow the TODOs to:

1. Import `FastMCP` and your `ProductsRepository`.
2. Instantiate the FastMCP app with a name and instructions block.
3. Add `@mcp.tool`-decorated functions for the four tools.
4. Expose the ASGI app via `mcp.http_app(path="/mcp", transport="streamable-http")`.

<details markdown="block">
<summary><strong>Expand this section to view the solution</strong></summary>

```python
"""Pepsico Products MCP server (FastMCP, streamable HTTP transport)."""

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


app = mcp.http_app(path="/mcp", transport="streamable-http")


def main() -> None:
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=int(os.getenv("PORT", "8001")))


if __name__ == "__main__":
    main()
```

</details>

### 03: Why these four tools?

| Tool | Job |
| ---- | --- |
| `list_categories` | Disambiguating user requests ("Do you mean beverages or snacks?") |
| `list_products(category)` | Browsing by category |
| `get_product(id)` | Following up on a specific SKU mentioned earlier |
| `search_products(text)` | Free-text natural-language requests |

We deliberately keep the surface **small and read-only**. MCP tools should be
*purposeful*; the model is much better at picking the right one when each tool
has a clear, single job.

The **docstring becomes the tool description** the LLM sees, and the Python
type hints become the JSON schema. That is why both matter as much as the
code.

## Next

Continue to [02.03 — Run the server locally](02_03_run_locally.md).

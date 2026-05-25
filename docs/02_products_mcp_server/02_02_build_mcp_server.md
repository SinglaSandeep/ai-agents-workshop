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
`src/mcp_servers/products/`. Try writing them yourself first — peek only
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

Open [src/mcp_servers/products/cosmos_repo.py](https://github.com/SinglaSandeep/ai-agents-workshop/blob/main/src/mcp_servers/products/cosmos_repo.py).
The skeleton already imports `get_container` from `src.common.cosmos` and
selects the products container in `__init__`. You just need to fill in each
query method **and emit one log line per query** via the `_log_query` helper
on the `zava.mcp.products.cosmos` logger so each tool call is auditable.


### 02: Implement `server.py`

Open [src/mcp_servers/products/server.py](https://github.com/SinglaSandeep/ai-agents-workshop/blob/main/src/mcp_servers/products/server.py).
Follow the TODOs to:

1. Import `FastMCP` and your `ProductsRepository`.
2. Instantiate the FastMCP app with a name and instructions block.
3. Add `@mcp.tool`-decorated functions for the four tools.
4. Expose the ASGI app via `mcp.http_app(path="/mcp", transport="streamable-http")`.


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

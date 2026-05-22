---
title: '2. Walk through the MCP server code'
layout: default
nav_order: 2
parent: 'Exercise 01: Products MCP Server'
---

# Task 01.02 — Understand the FastMCP Server

This is a reading-and-understanding task — no commands to run.

## File layout

```
src/mcp_servers/products/
├── __init__.py
├── server.py            # FastMCP app + tool decorators
├── cosmos_repo.py       # Read-only Cosmos DB queries
├── Dockerfile           # Container image (used in 01.04)
├── requirements.txt
└── seed/
    ├── products_seed.json
    └── seed_cosmos.py
```

## `cosmos_repo.py`

A thin repository over the `products` container. It uses **`DefaultAzureCredential`**
(no keys) and only ever issues SELECT queries. Every method returns plain
Python `dict`s so the MCP server can JSON-serialize them straight back to the
caller.

Key methods:

| Method | Cosmos query |
| ------ | ------------ |
| `list_categories()` | `SELECT DISTINCT VALUE c.category FROM c` |
| `list_products(category, limit)` | `SELECT TOP @limit ... FROM c [WHERE LOWER(c.category) = LOWER(@cat)]` |
| `get_product(product_id)` | `read_item(item=id, partition_key=id)` |
| `search_products(text, limit)` | `CONTAINS` over name / description / brand |

## `server.py`

The MCP server is built with [`fastmcp`](https://github.com/jlowin/fastmcp).
The pattern is:

```python
from fastmcp import FastMCP

mcp = FastMCP(name="pepsico-products", instructions="...")

@mcp.tool
def list_categories() -> list[str]:
    """List all distinct product categories ..."""
    return _repo().list_categories()
```

Each `@mcp.tool` becomes a JSON-RPC method that the MCP transport advertises
to the client. The **docstring becomes the tool description** the LLM sees,
and Python type hints become the JSON schema.

At the bottom we expose the server as an **ASGI app over streamable HTTP**:

```python
app = mcp.http_app(path="/mcp", transport="streamable-http")
```

`streamable-http` is the transport Foundry's `MCPTool` uses — it's HTTP POST
with optional server-sent-event responses.

## Why these four tools?

| Tool | What the agent will use it for |
| ---- | ------------------------------ |
| `list_categories` | Disambiguating user requests ("Do you mean beverages or snacks?") |
| `list_products(category)` | Browsing by category |
| `get_product(id)` | Following up on a specific SKU mentioned earlier |
| `search_products(text)` | Free-text natural-language requests |

We deliberately keep the surface **small and read-only**. MCP tools should be
*purposeful*; the model is much better at picking the right one when each tool
has a clear job.

## Success criteria

{: .success }
> - You can describe what each of the four tools does
> - You understand that FastMCP turns docstrings + type hints into the
>   schema the LLM sees
> - You know which transport the server uses (`streamable-http`) and where
>   the MCP endpoint is mounted (`/mcp`)

## Next

[01.03 — Run the server locally](01_03_run_locally.md).

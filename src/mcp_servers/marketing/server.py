"""Pepsico **Marketing** MCP server (FastMCP, streamable HTTP transport).

You build this file out in **Exercise 04**. When complete it will expose
five Cosmos DB-backed MCP tools that the Marketing Foundry agent (Exercise 05)
will call:

* ``list_active_campaigns(limit=20)``
* ``list_campaigns_by_brand(brand, limit=20)``
* ``get_campaign(campaign_id)``
* ``search_campaigns(text, limit=10)``
* ``campaign_performance(campaign_id)``

Run locally (after you complete Exercise 04):

    uvicorn src.mcp_servers.marketing.server:app --port 8002

Reference solution: ``solution/mcp_servers/marketing/server.py``.
"""

from __future__ import annotations

import os

# TODO (Exercise 04): import FastMCP and your MarketingRepository.
#   from fastmcp import FastMCP
#   from .cosmos_repo import MarketingRepository


# TODO (Exercise 04): instantiate the FastMCP app with a name + instructions.
#   mcp = FastMCP(name="pepsico-marketing", instructions="...")


# TODO (Exercise 04): declare the five `@mcp.tool` functions. Mirror the
# pattern used for the Products MCP server in Exercise 02.


# TODO (Exercise 04): expose the streamable-HTTP ASGI app.
#   app = mcp.http_app(path="/mcp", transport="streamable-http")
app = None  # replaced in Exercise 04


def main() -> None:
    import uvicorn

    if app is None:
        raise RuntimeError(
            "The Marketing MCP server is not implemented yet — complete "
            "Exercise 04 to build it."
        )
    uvicorn.run(app, host="0.0.0.0", port=int(os.getenv("PORT", "8002")))


if __name__ == "__main__":
    main()

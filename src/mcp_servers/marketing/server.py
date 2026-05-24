"""Zava Marketing MCP server (FastMCP, streamable HTTP transport).

You build this file out in **Exercise 04**. When complete, it will expose
six Cosmos DB-backed MCP tools that the Marketing Foundry agent (Exercise 05)
will call:

* ``list_active_campaigns(limit=20)``
* ``list_campaigns_by_category(category, limit=20)``
* ``list_campaigns_by_store(store_id, limit=20)``    — cross-store join
* ``get_campaign(campaign_id)``                       — id pattern ``ZV-CMP-YYYY-NNN``
* ``search_campaigns(text, limit=10)``
* ``campaign_performance(campaign_id)``               — KPIs

Run locally:
    uvicorn src.mcp_servers.marketing.server:app --port 8002

Reference solution: ``solution/mcp_servers/marketing/server.py``.
"""

from __future__ import annotations

import os

# TODO (Exercise 04): import FastMCP and your MarketingRepository.
#   from fastmcp import FastMCP
#   from .cosmos_repo import MarketingRepository


# TODO (Exercise 04): instantiate FastMCP with task-oriented `instructions`
# that explain the Zava entities (categories, stores, ZV-CMP-YYYY-NNN ids)
# and which tool to pick for which kind of question.


# TODO (Exercise 04): @mcp.tool functions for each of the six tools.
# Annotate parameters with `Annotated[..., Field(...)]` so the LLM gets
# the regex pattern for campaign_id, the allowed category_id values, and
# the allowed store_id values.


# TODO (Exercise 04): expose as ASGI:
#   app = mcp.http_app(path="/mcp", transport="streamable-http")
app = None  # replaced in Exercise 04


def main() -> None:
    """Entry point for the ``zava-marketing-mcp`` console script."""
    import uvicorn

    if app is None:
        raise RuntimeError(
            "The Marketing MCP server is not implemented yet — complete "
            "Exercise 04 to build it."
        )
    uvicorn.run(app, host="0.0.0.0", port=int(os.getenv("PORT", "8002")))


if __name__ == "__main__":
    main()

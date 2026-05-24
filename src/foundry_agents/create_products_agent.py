"""Create the Zava Products Foundry Prompt Agent."""

from __future__ import annotations

import logging

from azure.ai.projects.models import MCPTool

from src.common.foundry_client import upsert_project_connection
from src.common.settings import get_settings

from ._common import create_or_update_agent

LOG = logging.getLogger(__name__)

INSTRUCTIONS = """You are the Zava Products Specialist.

Zava is a Pacific Northwest DIY hardware retailer with 7 physical stores
(seattle, bellevue, tacoma, redmond, kirkland, spokane, everett) plus an
online fulfillment center. SKUs follow the pattern `ZV-<CAT>-NNN`
(`ZV-PNT-001` for paint, `ZV-PWT-014` for power-tools, etc.). Categories
are: paint, power-tools, hand-tools, garden, lumber, electrical, plumbing,
hardware.

You have access to the `zava-products` MCP server which exposes:
  - list_categories()
  - list_products(category, limit)
  - get_product(product_id)
  - search_products(text, limit)
  - inventory_by_store(product_id)
  - low_stock_alerts(store_id, limit)

Rules:
1. Pick the most specific tool for the user's question. For per-store
   inventory questions use `inventory_by_store` or `low_stock_alerts`.
2. Only answer using data returned by the tools — never invent products,
   SKUs, prices, sizes, or on-hand quantities.
3. When you cite a product, include its `id` (e.g. `ZV-PNT-001`) and
   `name`. When discussing inventory always state the `store_id`.
4. If the catalog has no match, say so plainly and suggest a related
   category.
"""


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    settings = get_settings()

    if not settings.products_mcp_url:
        raise RuntimeError(
            "PRODUCTS_MCP_URL is empty. Deploy the Products MCP server in Exercise 02 first."
        )

    # 1. Project connection that owns the URL + auth.
    #    The Container App MCP server is currently unauthenticated, so the
    #    connection is anonymous. Using ProjectManagedIdentity with a
    #    Microsoft audience (e.g. management.azure.com) triggers Foundry's
    #    safety check: "Cannot pass Microsoft token to untrusted MCP endpoint".
    upsert_project_connection(
        connection_name=settings.products_mcp_connection_name,
        category="RemoteTool",
        target=settings.products_mcp_url,
        auth_type="None",
        metadata={"ApiType": "MCP"},
    )

    # 2. The agent's view of that connection.
    products_tool = MCPTool(
        server_label="zava-products",
        server_url=settings.products_mcp_url,
        require_approval="never",
        project_connection_id=settings.products_mcp_connection_name,
    )

    create_or_update_agent(
        agent_name=settings.products_agent_name,
        instructions=INSTRUCTIONS,
        tools=[products_tool],
        model=settings.azure_ai_model_deployment,
        description="Zava Products specialist (MCP-backed by Cosmos DB).",
    )


if __name__ == "__main__":
    main()

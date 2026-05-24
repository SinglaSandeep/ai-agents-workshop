"""Create the Pepsico Products Foundry Prompt Agent."""

from __future__ import annotations

import logging

from azure.ai.projects.models import MCPTool

from src.common.foundry_client import upsert_project_connection
from src.common.settings import get_settings

from ._common import create_or_update_agent

LOG = logging.getLogger(__name__)

INSTRUCTIONS = """You are the Pepsico Products Specialist.

You have access to the `pepsico-products` MCP server which exposes:
  - list_categories()
  - list_products(category, limit)
  - get_product(product_id)
  - search_products(text, limit)

Rules:
1. Pick the most specific tool for the user's question.
2. Only answer using data returned by the tools — never invent products,
   SKUs, prices, or sizes.
3. When you cite a product, include its `id` (e.g. `PEP-001`) and `name`.
4. If the catalog has no match, say so plainly and suggest a related category.
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
        server_label="pepsico-products",
        server_url=settings.products_mcp_url,
        require_approval="never",
        project_connection_id=settings.products_mcp_connection_name,
    )

    create_or_update_agent(
        agent_name=settings.products_agent_name,
        instructions=INSTRUCTIONS,
        tools=[products_tool],
        model=settings.azure_ai_model_deployment,
        description="Pepsico Products specialist (MCP-backed by Cosmos DB).",
    )


if __name__ == "__main__":
    main()

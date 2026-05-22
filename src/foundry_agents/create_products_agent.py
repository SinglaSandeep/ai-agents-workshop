"""Create the Pepsico **Products** Foundry Prompt Agent.

You implement this script in **Exercise 03 / Task 03.02**. It does two
things:

1. Registers (or updates) a Foundry project **connection** that points at the
   Products MCP server you deployed in Exercise 02.
2. Creates a new version of the Products Prompt Agent, attaching the MCP
   server as an ``MCPTool``.

Run (after you complete the TODOs):

    python -m src.foundry_agents.create_products_agent

Reference solution: ``solution/foundry_agents/create_products_agent.py``.
"""

from __future__ import annotations

import logging

# TODO (Exercise 03): import MCPTool and the helpers below.
#   from azure.ai.projects.models import MCPTool
#   from src.common.foundry_client import upsert_project_connection
#   from src.common.settings import get_settings
#   from ._common import create_or_update_agent

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

    # TODO (Exercise 03 / Task 03.02):
    #
    # 1. Load settings and validate that PRODUCTS_MCP_URL is populated.
    # 2. Call `upsert_project_connection` with:
    #       category="RemoteTool",
    #       target=settings.products_mcp_url,
    #       auth_type="ProjectManagedIdentity",
    #       audience="https://management.azure.com/",
    #       metadata={"ApiType": "MCP"},
    # 3. Build an `MCPTool` referencing the new connection.
    # 4. Call `create_or_update_agent(agent_name=settings.products_agent_name,
    #       instructions=INSTRUCTIONS, tools=[products_tool], ...)`.

    raise NotImplementedError(
        "create_products_agent is not implemented yet — complete Exercise 03."
    )


if __name__ == "__main__":
    main()

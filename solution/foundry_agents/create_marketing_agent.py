"""Create the Marketing Foundry Prompt Agent with TWO tools:
  - the Marketing MCP server (Cosmos-backed campaign data)
  - the Grounding-with-Bing-Search web search tool

Pre-requisites:
- Marketing MCP container app deployed (Exercise 02) and `MARKETING_MCP_URL` set.
- A Grounding-with-Bing-Search resource exists AND a Foundry **connection** to
  it has been registered on your project with the name in
  `BING_GROUNDING_CONNECTION_NAME` (see docs/05_marketing_foundry_agent/05_01_register_mcp_and_bing.md).

Run:
    python -m src.foundry_agents.create_marketing_agent
"""

from __future__ import annotations

import logging

from azure.ai.projects.models import MCPTool, WebSearchTool

from src.common.foundry_client import upsert_project_connection
from src.common.settings import get_settings

from ._common import create_or_update_agent

LOG = logging.getLogger(__name__)

INSTRUCTIONS = """You are the Pepsico Marketing Specialist.

You have two tools:

1. The `pepsico-marketing` MCP server, which is the source of truth for ALL
   Pepsico campaign data (status, budget, channels, KPIs, etc.). Use it first
   for any question about Pepsico campaigns.

2. The web search tool (Grounding with Bing). Use it ONLY for:
   - Live news about Pepsico brands or competitors.
   - Public market context (industry trends, competitor announcements).
   - Any question that requires information after the model's training cutoff.

Rules:
- Never make up Pepsico campaign data. If the MCP tool returns nothing, say so.
- When you cite the web, include the URL.
- Always finish with a one-line summary of which tool you used and why.
"""


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    settings = get_settings()

    if not settings.marketing_mcp_url:
        raise RuntimeError(
            "MARKETING_MCP_URL is empty. Deploy the Marketing MCP server (Exercise 02) first."
        )

    # 1. Marketing MCP project connection.
    upsert_project_connection(
        connection_name=settings.marketing_mcp_connection_name,
        category="RemoteTool",
        target=settings.marketing_mcp_url,
        auth_type="ProjectManagedIdentity",
        audience="https://management.azure.com/",
        metadata={"ApiType": "MCP"},
    )

    marketing_tool = MCPTool(
        server_label="pepsico-marketing",
        server_url=settings.marketing_mcp_url,
        require_approval="never",
        project_connection_id=settings.marketing_mcp_connection_name,
    )

    # 2. Bing Grounding web-search tool. The Bing CONNECTION is created out of
    #    band (see docs/05_marketing_foundry_agent/05_01_register_mcp_and_bing.md);
    #    we just reference it by name here.
    web_search_tool = WebSearchTool()

    create_or_update_agent(
        agent_name=settings.marketing_agent_name,
        instructions=INSTRUCTIONS,
        tools=[marketing_tool, web_search_tool],
        description="Pepsico Marketing specialist (Cosmos-backed MCP + Bing Grounding).",
    )


if __name__ == "__main__":
    main()

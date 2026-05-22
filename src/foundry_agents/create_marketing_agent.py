"""Create the Pepsico **Marketing** Foundry Prompt Agent.

You implement this script in **Exercise 05**. The Marketing agent gets two
tools: the Marketing MCP server (Cosmos-backed campaign data) **and** the
Grounding-with-Bing-Search web tool.

Pre-requisites:

* Marketing MCP container app deployed (Exercise 04) and ``MARKETING_MCP_URL``
  set in ``.env``.
* A Grounding-with-Bing-Search resource exists *and* a Foundry connection
  to it has been registered on your project with the name in
  ``BING_GROUNDING_CONNECTION_NAME``.

Run:

    python -m src.foundry_agents.create_marketing_agent

Reference solution: ``solution/foundry_agents/create_marketing_agent.py``.
"""

from __future__ import annotations

import logging

# TODO (Exercise 05): import MCPTool, WebSearchTool, helpers.
#   from azure.ai.projects.models import MCPTool, WebSearchTool
#   from src.common.foundry_client import upsert_project_connection
#   from src.common.settings import get_settings
#   from ._common import create_or_update_agent

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

    # TODO (Exercise 05):
    #
    # 1. Load settings + validate MARKETING_MCP_URL.
    # 2. Upsert the Marketing MCP project connection.
    # 3. Build an MCPTool pointing at it.
    # 4. Build a WebSearchTool() (it picks up the Bing connection by name
    #    via the BING_GROUNDING_CONNECTION_NAME setting).
    # 5. Call `create_or_update_agent(..., tools=[marketing_tool, web_search_tool])`.

    raise NotImplementedError(
        "create_marketing_agent is not implemented yet — complete Exercise 05."
    )


if __name__ == "__main__":
    main()

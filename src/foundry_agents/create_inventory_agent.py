"""Create the Zava Inventory Insights Foundry Prompt Agent."""

from __future__ import annotations

import logging

from azure.ai.projects.models import MCPTool

from src.common.foundry_client import upsert_project_connection
from src.common.settings import get_settings
from src.prompts import load_prompt

from ._common import create_or_update_agent

LOG = logging.getLogger(__name__)

INSTRUCTIONS = load_prompt("inventory_agent")


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    settings = get_settings()

    if not settings.inventory_mcp_url:
        raise RuntimeError(
            "INVENTORY_MCP_URL is empty. Deploy the Inventory MCP server first."
        )

    upsert_project_connection(
        connection_name=settings.inventory_mcp_connection_name,
        category="RemoteTool",
        target=settings.inventory_mcp_url,
        auth_type="None",
        metadata={"ApiType": "MCP"},
    )

    inventory_tool = MCPTool(
        server_label="zava-inventory",
        server_url=settings.inventory_mcp_url,
        require_approval="never",
        project_connection_id=settings.inventory_mcp_connection_name,
    )

    create_or_update_agent(
        agent_name=settings.inventory_agent_name,
        instructions=INSTRUCTIONS,
        tools=[inventory_tool],
        model=settings.azure_ai_model_deployment,
        description="Zava distributor-inventory insights specialist (MCP-backed by Cosmos DB).",
    )


if __name__ == "__main__":
    main()

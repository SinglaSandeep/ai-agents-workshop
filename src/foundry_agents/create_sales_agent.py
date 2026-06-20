"""Create the Zava Sales Insights Foundry Prompt Agent."""

from __future__ import annotations

import logging

from azure.ai.projects.models import MCPTool

from src.common.foundry_client import upsert_project_connection
from src.common.settings import get_settings
from src.prompts import load_prompt

from ._common import create_or_update_agent

LOG = logging.getLogger(__name__)

INSTRUCTIONS = load_prompt("sales_agent")


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    settings = get_settings()

    if not settings.sales_mcp_url:
        raise RuntimeError(
            "SALES_MCP_URL is empty. Deploy the Sales MCP server first."
        )

    upsert_project_connection(
        connection_name=settings.sales_mcp_connection_name,
        category="RemoteTool",
        target=settings.sales_mcp_url,
        auth_type="None",
        metadata={"ApiType": "MCP"},
    )

    sales_tool = MCPTool(
        server_label="zava-sales",
        server_url=settings.sales_mcp_url,
        require_approval="never",
        project_connection_id=settings.sales_mcp_connection_name,
    )

    create_or_update_agent(
        agent_name=settings.sales_agent_name,
        instructions=INSTRUCTIONS,
        tools=[sales_tool],
        model=settings.azure_ai_model_deployment,
        description="Zava Sales insights specialist (MCP-backed by Cosmos DB).",
    )


if __name__ == "__main__":
    main()

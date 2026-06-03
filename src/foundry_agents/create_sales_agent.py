"""Create the Zava Sales Insights Foundry Prompt Agent."""

from __future__ import annotations

import logging

from azure.ai.projects.models import MCPTool

from src.common.foundry_client import upsert_project_connection
from src.common.settings import get_settings

from ._common import create_or_update_agent

LOG = logging.getLogger(__name__)

INSTRUCTIONS = """You are the Zava Sales Insights Specialist. Zava: PNW DIY
hardware retailer; stores seattle, bellevue, tacoma, redmond, kirkland,
spokane, everett (+online); regions north/south/east/online. Categories:
paint, power-tools, hand-tools, garden, lumber, electrical, plumbing,
hardware. SKUs `ZV-<CAT>-NNN`.

Tools (`zava-sales` MCP): list_dimensions, revenue_summary(group_by, limit),
monthly_trend(category, store_id), top_products(metric, limit, ascending),
sales_for_product(product_id), get_order(order_id).

Turn data into decision-ready insights:
- Pick the most specific tool (revenue_summary/top_products for what's
  selling or declining; monthly_trend for direction).
- Quantify moves with the dimension (e.g. "garden +38% over 3 months").
- Use only tool-returned values; never invent figures, ids, or percentages.
- Reply with 1-3 short insight bullets for the Action agent.
- Be terse: no preamble, no restating the question.
"""


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

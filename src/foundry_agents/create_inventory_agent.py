"""Create the Zava Inventory Insights Foundry Prompt Agent."""

from __future__ import annotations

import logging

from azure.ai.projects.models import MCPTool

from src.common.foundry_client import upsert_project_connection
from src.common.settings import get_settings

from ._common import create_or_update_agent

LOG = logging.getLogger(__name__)

INSTRUCTIONS = """You are the Zava Inventory Insights Specialist.
Distributors -> warehouses: DIST-NW-01 Cascade (north) -> WH-SEA, WH-BEL;
DIST-SW-02 Rainier (south) -> WH-TAC; DIST-E-03 Inland NW (east) -> WH-SPO;
DIST-ON-04 Zava Direct (online) -> WH-DC1, WH-DC2. Categories: paint,
power-tools, hand-tools, garden, lumber, electrical, plumbing, hardware.
SKUs `ZV-<CAT>-NNN`.

Tools (`zava-inventory` MCP): list_distributors, stock_status_summary(region),
low_stock(region, warehouse_id, limit), overstock(limit),
reorder_recommendations(limit), inventory_for_product(product_id),
inventory_trend(warehouse_id, product_id), get_inventory(inventory_id).

Surface stock-health insights:
- stock_status_summary for overview, then low_stock/overstock/
  reorder_recommendations to drill into problems.
- Always report weeks_of_cover and the warehouse/distributor.
- Use only tool-returned values; never invent quantities or ids.
- product_ids look like `ZV-PWT-014` (3-letter category code). Never guess
  one or build it from a product name. If you only have a product name and
  no exact `product_id`, use region/category tools (stock_status_summary,
  low_stock, reorder_recommendations) instead of inventory_for_product.
- Reply with 1-3 short insight bullets for the Action agent.
- Be terse: no preamble, no restating the question.
"""


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

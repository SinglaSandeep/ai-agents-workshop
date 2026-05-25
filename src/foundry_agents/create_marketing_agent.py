"""Register the Foundry **Marketing Prompt Agent**.

Creates / updates `MARKETING_AGENT_NAME` (default `zava-marketing-agent`) as
a Foundry Prompt Agent wired to:

  - the Marketing MCP server from Exercise 04 (Cosmos campaign records),
  - the Foundry Code Interpreter tool,
  - the Marketing Foundry IQ knowledge base from `setup_marketing_knowledge_base`.

This is the **only** Marketing-agent path in the workshop — there is no
Foundry-hosted Agent-Framework variant. Anything that resolves marketing by
name (orchestrator, DevUI, evals) just works.

Pre-reqs:
  - `MARKETING_MCP_URL` set in `.env` (Exercise 04).
  - Marketing KB seeded (`python -m src.knowledge_seed.setup_marketing_knowledge_base`).

Run:

    python -m src.foundry_agents.create_marketing_agent
"""

from __future__ import annotations

import logging

from azure.ai.projects.models import (
    CodeInterpreterTool,
    MCPTool,
)

from src.common.foundry_client import upsert_project_connection
from src.common.settings import get_settings

from ._common import create_or_update_agent

LOG = logging.getLogger(__name__)

INSTRUCTIONS = """You are the Zava Marketing Specialist.

Zava is a Pacific Northwest DIY hardware retailer with 7 physical stores
(seattle, bellevue, tacoma, redmond, kirkland, spokane, everett) plus an
online fulfillment center. Campaign IDs follow `ZV-CMP-YYYY-NNN`.

You have the following tools:

1. `zava-marketing` MCP — authoritative campaign records (status, budget,
   channels, KPIs, featured product_ids, target store_ids, category_id)
   backed by Cosmos DB. Prefer the most specific tool:
     - `list_campaigns_by_store` / `list_campaigns_by_category` when the
       user names a store or category
     - `get_campaign(campaign_id)` for a single campaign
     - `list_campaigns(status)` / `search_campaigns(text)` otherwise
2. `code_interpreter` — sandboxed Python for ad-hoc analysis on the
   campaign data returned by the MCP (totals, comparisons, charts).
3. `marketing-knowledge-base` Foundry IQ KB — `knowledge_base_retrieve`
   over indexed Zava marketing briefs and campaign post-mortems. When the
   user references a specific store_id or category_id, pass it as a
   retrieval filter.

Rules:
1. Never invent Zava campaign data, SKUs, or stores. Prefer the MCP for
   structured facts and the KB for narrative briefs.
2. Always cite `campaign_id`, `store_id`, `category_id`, or `product_id`
   when referencing structured data.
3. You do NOT have a web-search tool. If the user asks for live news or
   competitor activity, say so plainly and offer to answer from the KB or
   MCP instead.
4. End every answer with a line: `Tools used: ...`.
"""


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    settings = get_settings()

    if not settings.marketing_mcp_url:
        raise RuntimeError(
            "MARKETING_MCP_URL is empty. Deploy the Marketing MCP server "
            "in Exercise 04 first."
        )
    if not settings.azure_search_endpoint:
        raise RuntimeError(
            "AZURE_SEARCH_ENDPOINT is empty. Run "
            "`python -m src.knowledge_seed.setup_marketing_knowledge_base` first."
        )
    if not settings.azure_ai_project_endpoint:
        raise RuntimeError("AZURE_AI_PROJECT_ENDPOINT must be set.")

    tools: list = []

    # 1) Marketing MCP server (Cosmos truth).
    upsert_project_connection(
        connection_name=settings.marketing_mcp_connection_name,
        category="RemoteTool",
        target=settings.marketing_mcp_url,
        auth_type="None",
        metadata={"ApiType": "MCP"},
    )
    tools.append(
        MCPTool(
            server_label="zava-marketing",
            server_url=settings.marketing_mcp_url,
            require_approval="never",
            project_connection_id=settings.marketing_mcp_connection_name,
        )
    )


    # 3) Code Interpreter (no connection required).
    tools.append(CodeInterpreterTool())

    # 4) Foundry IQ KB MCP (Marketing briefs + post-mortems).
    kb_url = (
        f"{settings.azure_search_endpoint.rstrip('/')}"
        f"/knowledgebases/{settings.marketing_kb_name}"
        "/mcp?api-version=2025-11-01-preview"
    )
    tools.append(
        MCPTool(
            server_label="marketing-knowledge-base",
            server_url=kb_url,
            require_approval="never",
            allowed_tools=["knowledge_base_retrieve"],
            project_connection_id=settings.marketing_kb_connection_name,
        )
    )

    create_or_update_agent(
        agent_name=settings.marketing_agent_name,
        instructions=INSTRUCTIONS,
        tools=tools,
        model=settings.azure_ai_model_deployment,
        description=(
            "Zava Marketing specialist (Foundry Prompt Agent). Wires "
            "Marketing MCP + Code Interpreter + Foundry IQ KB."
        ),
    )


if __name__ == "__main__":
    main()


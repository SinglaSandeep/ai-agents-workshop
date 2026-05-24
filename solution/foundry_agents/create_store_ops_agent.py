"""Create the **Zava Store-Ops** Foundry Prompt Agent grounded by Foundry IQ.

Run AFTER `setup_store_ops_knowledge_base.py` so the KB and project
connection exist.

    python -m src.foundry_agents.create_store_ops_agent
"""

from __future__ import annotations

import logging

from azure.ai.projects.models import MCPTool

from src.common.settings import get_settings

from ._common import create_or_update_agent

LOG = logging.getLogger(__name__)

INSTRUCTIONS = """You are the Zava Store-Operations Assistant.

Zava is a Pacific Northwest DIY hardware retailer with 7 physical stores
(seattle, bellevue, tacoma, redmond, kirkland, spokane, everett) plus an
online fulfillment center (store_id = 'online'). You answer questions
from store managers and associates about company policies, safety, returns,
HR, onboarding, and store-specific operating procedures.

Your only source of truth is the connected Foundry IQ knowledge base of
Zava store-ops Markdown documents. For every answer you MUST:

1. Identify the relevant `store_id` from the user's question. If they
   reference a specific store (e.g., "the Seattle store"), restrict
   retrieval to that store_id; otherwise default to chain-wide docs
   (store_id = 'all'). Pass the filter to the `knowledge_base_retrieve`
   tool using its filter argument.
2. Call `knowledge_base_retrieve` with a focused question.
3. Answer only from the retrieved content. If the answer is not there,
   say: "I could not find this in the current Zava store-ops knowledge
   base. Please escalate to your district manager."
4. When the answer touches on discount approvals, returns, or safety,
   cite the **exact policy section** (e.g., 'Discount Approval Matrix:
   11-20% band').
5. End every answer with a `Sources:` line listing the cited document
   filenames.
"""


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    settings = get_settings()

    if not settings.azure_search_endpoint:
        raise RuntimeError("AZURE_SEARCH_ENDPOINT must be set.")

    mcp_endpoint = (
        f"{settings.azure_search_endpoint.rstrip('/')}"
        f"/knowledgebases/{settings.store_ops_kb_name}/mcp?api-version=2025-11-01-preview"
    )

    store_ops_kb_tool = MCPTool(
        server_label="store-ops-knowledge-base",
        server_url=mcp_endpoint,
        require_approval="never",
        allowed_tools=["knowledge_base_retrieve"],
        project_connection_id=settings.store_ops_kb_connection_name,
    )

    create_or_update_agent(
        agent_name=settings.store_ops_agent_name,
        instructions=INSTRUCTIONS,
        tools=[store_ops_kb_tool],
        description=(
            "Zava store-operations specialist grounded by Foundry IQ. "
            "Handles policies, safety, returns, HR, and per-store handbooks. "
            "Scopes retrieval by store_id when the user references a specific store."
        ),
    )


if __name__ == "__main__":
    main()

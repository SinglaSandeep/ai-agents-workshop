"""Create the Zava **Store-Ops** Foundry Prompt Agent grounded by Foundry IQ.

You implement this script in **Exercise 06 / Task 06.02**. Run only AFTER
``setup_store_ops_knowledge_base.py`` (Task 06.01) so the knowledge base
and the project connection already exist.

Run:

    python -m src.foundry_agents.create_store_ops_agent

Reference solution: ``solution/foundry_agents/create_store_ops_agent.py``.
"""

from __future__ import annotations

import logging

# TODO (Exercise 06): import MCPTool + helpers.
#   from azure.ai.projects.models import MCPTool
#   from src.common.settings import get_settings
#   from ._common import create_or_update_agent

LOG = logging.getLogger(__name__)


INSTRUCTIONS = """You are the Zava Store-Operations Assistant.

Zava is a Pacific Northwest DIY hardware retailer with 7 physical stores
(seattle, bellevue, tacoma, redmond, kirkland, spokane, everett) plus an
online fulfillment center.

Your only source of truth is the connected Foundry IQ knowledge base of
Zava store-ops Markdown documents. For every answer you MUST:

1. Identify the relevant `store_id` from the user's question. If they
   reference a specific store, restrict retrieval to that store_id;
   otherwise default to chain-wide docs (store_id = 'all').
2. Call `knowledge_base_retrieve` with a focused question.
3. Answer only from the retrieved content. If the answer is not there,
   say: "I could not find this in the current Zava store-ops knowledge
   base. Please escalate to your district manager."
4. End every answer with a `Sources:` line listing the cited document
   filenames.
"""


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")

    # TODO (Exercise 06):
    #
    # 1. Validate AZURE_SEARCH_ENDPOINT is set.
    # 2. Build the MCP endpoint URL for the store-ops knowledge base:
    #       f"{settings.azure_search_endpoint.rstrip('/')}"
    #       f"/knowledgebases/{settings.store_ops_kb_name}/mcp?api-version=2025-11-01-preview"
    # 3. Construct an MCPTool with `allowed_tools=["knowledge_base_retrieve"]`
    #    and `project_connection_id=settings.store_ops_kb_connection_name`.
    # 4. Call `create_or_update_agent(..., tools=[store_ops_kb_tool])`.

    raise NotImplementedError(
        "create_store_ops_agent is not implemented yet — complete Exercise 06."
    )


if __name__ == "__main__":
    main()

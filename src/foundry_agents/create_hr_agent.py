"""Create the **HR** Foundry Prompt Agent grounded by a Foundry IQ knowledge base.

Run AFTER `setup_hr_knowledge_base.py` so the KB and project connection exist.

    python -m src.foundry_agents.create_hr_agent
"""

from __future__ import annotations

import logging

from azure.ai.projects.models import MCPTool

from src.common.settings import get_settings

from ._common import create_or_update_agent

LOG = logging.getLogger(__name__)

INSTRUCTIONS = """You are the Pepsico HR Assistant.

Your only source of truth is the connected Foundry IQ knowledge base of Pepsico HR
policies. For every answer you MUST:

1. Call the `knowledge_base_retrieve` tool with a focused question.
2. Answer only from the retrieved content. If the answer is not there, say:
   "I could not find this in the current Pepsico HR knowledge base. Please contact
   your HR business partner."
3. End every answer with a `Sources:` line listing the cited document filenames.
"""


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    settings = get_settings()

    if not settings.azure_search_endpoint:
        raise RuntimeError("AZURE_SEARCH_ENDPOINT must be set.")

    mcp_endpoint = (
        f"{settings.azure_search_endpoint.rstrip('/')}"
        f"/knowledgebases/{settings.hr_kb_name}/mcp?api-version=2025-11-01-preview"
    )

    hr_kb_tool = MCPTool(
        server_label="hr-knowledge-base",
        server_url=mcp_endpoint,
        require_approval="never",
        allowed_tools=["knowledge_base_retrieve"],
        project_connection_id=settings.hr_kb_connection_name,
    )

    create_or_update_agent(
        agent_name=settings.hr_agent_name,
        instructions=INSTRUCTIONS,
        tools=[hr_kb_tool],
        description="Pepsico HR specialist grounded by Foundry IQ.",
    )


if __name__ == "__main__":
    main()

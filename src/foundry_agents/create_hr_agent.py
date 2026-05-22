"""Create the Pepsico **HR** Foundry Prompt Agent grounded by Foundry IQ.

You implement this script in **Exercise 06 / Task 06.02**. Run only AFTER
``setup_hr_knowledge_base.py`` (Task 06.01) so the knowledge base and the
project connection already exist.

Run:

    python -m src.foundry_agents.create_hr_agent

Reference solution: ``solution/foundry_agents/create_hr_agent.py``.
"""

from __future__ import annotations

import logging

# TODO (Exercise 06): import MCPTool + helpers.
#   from azure.ai.projects.models import MCPTool
#   from src.common.settings import get_settings
#   from ._common import create_or_update_agent

LOG = logging.getLogger(__name__)


INSTRUCTIONS = """You are the Pepsico HR Assistant.

Your only source of truth is the connected Foundry IQ knowledge base of
Pepsico HR policies. For every answer you MUST:

1. Call the `knowledge_base_retrieve` tool with a focused question.
2. Answer only from the retrieved content. If the answer is not there, say:
   "I could not find this in the current Pepsico HR knowledge base. Please
   contact your HR business partner."
3. End every answer with a `Sources:` line listing the cited document
   filenames.
"""


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")

    # TODO (Exercise 06):
    #
    # 1. Validate AZURE_SEARCH_ENDPOINT is set.
    # 2. Build the MCP endpoint URL for the HR knowledge base:
    #       f"{settings.azure_search_endpoint.rstrip('/')}"
    #       f"/knowledgebases/{settings.hr_kb_name}/mcp?api-version=2025-11-01-preview"
    # 3. Construct an MCPTool with `allowed_tools=["knowledge_base_retrieve"]`
    #    and `project_connection_id=settings.hr_kb_connection_name`.
    # 4. Call `create_or_update_agent(..., tools=[hr_kb_tool])`.

    raise NotImplementedError(
        "create_hr_agent is not implemented yet — complete Exercise 06."
    )


if __name__ == "__main__":
    main()

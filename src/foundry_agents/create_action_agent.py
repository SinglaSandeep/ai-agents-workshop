"""Create the **Action Recommender** Foundry Prompt Agent.

This agent sits downstream of the specialist agents (sales, inventory,
marketing) and turns their INSIGHTS into concrete, prioritised OPERATIONAL
ACTIONS — the "Action" half of the Insights-to-Action workflow. It is the
FINAL agent in the flow: it also writes the user-facing reply (with an
optional chart spec the front end renders), so there is no separate response
generator. It owns the Foundry **Code Interpreter** tool because it has the
full cross-domain context (sales + inventory + marketing) needed to compute
consolidated figures.

    python -m src.foundry_agents.create_action_agent
"""

from __future__ import annotations

import logging

from azure.ai.projects.models import CodeInterpreterTool

from src.common.settings import get_settings
from src.prompts import load_prompt

from ._common import create_or_update_agent

LOG = logging.getLogger(__name__)

INSTRUCTIONS = load_prompt("action_agent")


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    settings = get_settings()
    create_or_update_agent(
        agent_name=settings.action_agent_name,
        instructions=INSTRUCTIONS,
        tools=[CodeInterpreterTool()],
        description="Zava action recommender + final responder (code interpreter).",
    )


if __name__ == "__main__":
    main()

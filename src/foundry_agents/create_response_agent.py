"""Create the **Response Generator** Foundry Prompt Agent.

Its job is to take the structured output of the Magentic orchestrator (the
specialist transcripts) and produce the final user-facing answer in a
consistent Zava voice.

    python -m src.foundry_agents.create_response_agent
"""

from __future__ import annotations

import logging

from src.common.settings import get_settings
from src.prompts import load_prompt

from ._common import create_or_update_agent

LOG = logging.getLogger(__name__)

INSTRUCTIONS = load_prompt("response_agent")


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    settings = get_settings()
    create_or_update_agent(
        agent_name=settings.response_agent_name,
        instructions=INSTRUCTIONS,
        tools=[],
        description="Zava final-answer synthesiser.",
    )


if __name__ == "__main__":
    main()

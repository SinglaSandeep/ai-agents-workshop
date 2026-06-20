"""Create the **Intent Detector** Foundry Prompt Agent.

This agent has NO tools. It classifies the user's latest message as either a
GENERAL conversational turn (greetings, thanks, small talk, "what can you do")
or a BUSINESS turn that needs the Zava sales / inventory / marketing / action
specialists. The orchestrator uses this single-word verdict to decide whether
to answer directly via the Response Generator or run the full Magentic flow.

    python -m src.foundry_agents.create_intent_agent
"""

from __future__ import annotations

import logging

from src.common.settings import get_settings
from src.prompts import load_prompt

from ._common import create_or_update_agent

LOG = logging.getLogger(__name__)

INSTRUCTIONS = load_prompt("intent_agent")


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    settings = get_settings()
    create_or_update_agent(
        agent_name=settings.intent_agent_name,
        instructions=INSTRUCTIONS,
        tools=[],
        description="Zava intent classifier (GENERAL vs BUSINESS).",
    )


if __name__ == "__main__":
    main()

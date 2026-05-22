"""Create the **Response Generator** Foundry Prompt Agent.

This agent has NO tools. Its only job is to take the structured output of the
Magentic orchestrator (the specialist transcripts) and produce the final
user-facing answer in a consistent Pepsico voice.

    python -m src.foundry_agents.create_response_agent
"""

from __future__ import annotations

import logging

from src.common.settings import get_settings

from ._common import create_or_update_agent

LOG = logging.getLogger(__name__)

INSTRUCTIONS = """You are the Pepsico Response Generator.

You receive a JSON object with the user's original question and the answers
produced by one or more specialists ("hr", "products", "marketing"). Produce
the final reply for the user.

Rules:
- Lead with a single direct sentence answering the question.
- Then 1-3 short paragraphs of supporting detail. Use bullet points if helpful.
- Merge information from multiple specialists when relevant; never invent facts.
- If specialists conflict, prefer Pepsico's internal sources (HR knowledge base,
  Products MCP, Marketing MCP) over web search.
- End with a `Sources:` line listing the specialists used (e.g. `Sources: hr, products`)
  and any URLs surfaced by the marketing agent.
- Tone: warm, professional, concise. Pepsico-internal employees are the audience.
"""


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    settings = get_settings()
    create_or_update_agent(
        agent_name=settings.response_agent_name,
        instructions=INSTRUCTIONS,
        tools=[],
        description="Pepsico final-answer synthesiser.",
    )


if __name__ == "__main__":
    main()

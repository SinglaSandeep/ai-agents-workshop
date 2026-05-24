"""Create the Zava **Response Generator** Foundry Prompt Agent.

This agent has NO tools — its only job is to take the structured output of
the Magentic orchestrator (the specialist transcripts) and produce the final
user-facing answer in a consistent Zava voice.

You implement this script in **Exercise 08**.

Run:

    python -m src.foundry_agents.create_response_agent

Reference solution: ``solution/foundry_agents/create_response_agent.py``.
"""

from __future__ import annotations

import logging

# TODO (Exercise 08): import helpers.
#   from src.common.settings import get_settings
#   from ._common import create_or_update_agent

LOG = logging.getLogger(__name__)


INSTRUCTIONS = """You are the Zava Response Generator.

You receive a JSON object with the user's original question and the answers
produced by one or more specialists ("store_ops", "products", "marketing"). Produce
the final reply for the user.

Rules:
- Lead with a single direct sentence answering the question.
- Then 1-3 short paragraphs of supporting detail. Use bullet points if helpful.
- Merge information from multiple specialists when relevant; never invent facts.
- If specialists conflict, prefer Zava's internal sources (Store-Ops knowledge base,
  Products MCP, Marketing MCP) over web search.
- End with a `Sources:` line listing the specialists used (e.g.
  `Sources: store_ops, products`) and any URLs surfaced by the marketing agent.
- Tone: warm, professional, concise. Zava store-team employees are the audience.
"""


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")

    # TODO (Exercise 08): call `create_or_update_agent` with
    #   agent_name=settings.response_agent_name, instructions=INSTRUCTIONS,
    #   tools=[].

    raise NotImplementedError(
        "create_response_agent is not implemented yet — complete Exercise 08."
    )


if __name__ == "__main__":
    main()

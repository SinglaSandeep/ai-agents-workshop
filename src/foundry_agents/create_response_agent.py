"""Create the **Response Generator** Foundry Prompt Agent.

This agent has NO tools. Its only job is to take the structured output of the
Magentic orchestrator (the specialist transcripts) and produce the final
user-facing answer in a consistent Zava voice.

    python -m src.foundry_agents.create_response_agent
"""

from __future__ import annotations

import logging

from src.common.settings import get_settings

from ._common import create_or_update_agent

LOG = logging.getLogger(__name__)

INSTRUCTIONS = """You are the Zava Response Generator. You receive the user's
question plus answers from the specialists ("sales", "inventory", "marketing")
and the "action" recommender. Produce the final reply.

- Open with one direct sentence answering the question.
- Then 1-2 short paragraphs or bullets of support. Surface the recommended
  ACTIONS prominently.
- Merge specialists; never invent facts. Prefer Zava internal sources over web.
- If quantitative data benefits from a visual (trends, comparisons, status
  breakdowns), add ONE chart as a fenced ```chart block using ONLY numbers
  from the transcripts. Omit it when there is nothing meaningful to plot.
  Place it after the prose and before `Sources:`. Schema:
  ```chart
  {"type":"bar|line|pie|doughnut","title":"...","labels":["..."],"datasets":[{"label":"...","data":[...]}]}
  ```
- End with a `Sources:` line listing the specialists used (+ any marketing URLs).
- Tone: warm, professional, concise. Keep the whole reply tight.
"""


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

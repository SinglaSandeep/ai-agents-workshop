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

from ._common import create_or_update_agent

LOG = logging.getLogger(__name__)

INSTRUCTIONS = """You are the Zava Action Recommender and final responder.
You get the user's question plus INSIGHTS from "sales", "inventory", and
"marketing". Convert them into prioritised operational ACTIONS and write the
final, polished, user-facing reply.

Think cross-domain: a sales trend + an inventory position + a campaign
usually imply one coordinated move.

WRITE A WELL-FORMATTED REPLY. The front end renders a small subset of
Markdown, so use ONLY these elements (do NOT use Markdown tables or links):
- `## Headings` for sections.
- **Bold** for labels/owners, *italics* for emphasis, `code` for SKUs/ids.
- `-` bullet lists and `1.` numbered lists.
- ONE fenced ```chart block for a visual when it helps.

Structure:
1. One direct sentence answering the question (no heading).
2. `## Recommended actions` — a numbered list of 2-5 items. Format each as:
   **<action>** — *Owner:* <Merchandising | Distributor Ops | Marketing |
   Store Manager> · *Priority:* <High | Medium | Low> · *Why:* <evidence,
   citing the specialist + figure/id>.
3. If quantitative data benefits from a visual (trends, comparisons, status
   breakdowns), add `## Snapshot` followed by ONE fenced ```chart block using
   ONLY numbers from the insights. Pick the right type (bar=compare,
   line=trend, pie/doughnut=share). Omit the section when nothing meaningful
   to plot. Schema:
   ```chart
   {"type":"bar|line|pie|doughnut","title":"...","labels":["..."],"datasets":[{"label":"...","data":[...]}]}
   ```
4. End with a `**Sources:**` line listing the specialists used.

Rules:
- Use only facts in the insights; never invent numbers, SKUs, stores, or
  campaigns.
- Prefer actions that connect MULTIPLE domains.
- Use `code_interpreter` ONLY to consolidate/rank the numbers already given
  (e.g. combine per-store figures, compute shares for a chart) — never
  fabricate inputs, and it must not draw images (the front end draws charts
  from the ```chart spec).
- If the insights support no action, say so plainly and name the missing data.
Keep it concise and scannable.
"""


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

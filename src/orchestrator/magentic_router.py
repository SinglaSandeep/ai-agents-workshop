"""Magentic orchestrator that coordinates the Pepsico Foundry agents.

You complete this file in **Exercise 07**. It will wrap the four Foundry
hosted agents (HR, Products, Marketing, Response Generator) as Microsoft
Agent Framework participants and let the ``MagenticBuilder`` planner decide
who to call, in what order, and how to synthesise the result.

The reference solution is in ``solution/orchestrator/magentic_router.py``.

Run (after you complete Exercise 07):

    python -m src.orchestrator.runner --query "What is our PTO policy?"
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field

from src.common.settings import get_settings  # noqa: F401  (used in solution)

LOG = logging.getLogger(__name__)


@dataclass
class OrchestratorResult:
    final_answer: str
    plan: list[str] = field(default_factory=list)
    transcripts: dict[str, str] = field(default_factory=dict)
    events: list[dict] = field(default_factory=list)


async def run_query(user_query: str) -> OrchestratorResult:
    """Plan + execute a query across the Pepsico specialist agents.

    TODO (Exercise 07): implement the Magentic orchestrator.

    High-level steps:

    1. Lazy-import ``agent_framework``, ``agent_framework.azure``,
       ``agent_framework.orchestrations.MagenticBuilder``, and
       ``azure.identity.aio.DefaultAzureCredential``.
    2. Open an ``AzureAIAgentClient`` against ``settings.azure_ai_project_endpoint``.
    3. Wrap each Foundry hosted agent (``hr``, ``products``, ``marketing``,
       ``response_generator``) as an ``Agent(agent_reference={"name": ...})``.
    4. Create a ``manager`` Agent with planning instructions.
    5. Build a workflow with
       ``MagenticBuilder(participants=[...], manager_agent=manager).build()``.
    6. Iterate ``workflow.run(user_query, stream=True)`` and accumulate the
       plan, transcripts, and events into an ``OrchestratorResult``.
    """

    raise NotImplementedError(
        "run_query() is not implemented yet — complete Exercise 07 to enable "
        "the Magentic orchestrator. The reference solution is in "
        "solution/orchestrator/magentic_router.py."
    )

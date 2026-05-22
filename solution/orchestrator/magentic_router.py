"""Magentic orchestrator that coordinates the Pepsico Foundry agents.

The orchestrator uses **Microsoft Agent Framework** (`agent-framework`) and
its `MagenticBuilder` planner. The four Foundry hosted agents (HR, Products,
Marketing, Response Generator) are exposed to the planner as *participants*;
the planner picks which to call, in what order, and synthesises the trail.

The participants are not local Python agents — they are **hosted Foundry
agents** created in Exercises 03-05 and 07. We wrap each one in a thin
`Agent` adaptor that delegates `.run()` to the Foundry Responses API.

Run:
    python -m src.orchestrator.runner --query "What is our PTO policy?"
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field

from src.common.settings import get_settings

LOG = logging.getLogger(__name__)


@dataclass
class OrchestratorResult:
    final_answer: str
    plan: list[str] = field(default_factory=list)
    transcripts: dict[str, str] = field(default_factory=dict)
    events: list[dict] = field(default_factory=list)


async def run_query(user_query: str) -> OrchestratorResult:
    """Plan + execute a query across the Pepsico specialist agents.

    Lazy-imports `agent-framework` so the rest of the workshop runs without
    the `framework` extra installed.
    """
    settings = get_settings()

    try:
        from agent_framework import Agent
        from agent_framework.azure import AzureAIAgentClient
        from agent_framework.orchestrations import MagenticBuilder
        from azure.identity.aio import DefaultAzureCredential
    except ImportError as exc:
        raise RuntimeError(
            'Install the framework extra: pip install -e ".[framework]"'
        ) from exc

    async with DefaultAzureCredential() as cred:
        async with AzureAIAgentClient(
            project_endpoint=settings.azure_ai_project_endpoint,
            model_deployment_name=settings.azure_ai_model_deployment,
            credential=cred,
        ) as client:
            hr = Agent(
                client=client,
                name="hr",
                description="Answers Pepsico HR policy, benefits, and handbook questions using the Foundry IQ knowledge base.",
                agent_reference={"name": settings.hr_agent_name, "type": "agent_reference"},
            )
            products = Agent(
                client=client,
                name="products",
                description="Answers questions about the Pepsico product catalog (SKU, brand, size, calories, price) using the Products MCP server.",
                agent_reference={"name": settings.products_agent_name, "type": "agent_reference"},
            )
            marketing = Agent(
                client=client,
                name="marketing",
                description="Answers questions about Pepsico marketing campaigns (status, KPIs, budgets, ROI) using the Marketing MCP server, and can search the web via Bing for live context.",
                agent_reference={"name": settings.marketing_agent_name, "type": "agent_reference"},
            )
            response_generator = Agent(
                client=client,
                name="response_generator",
                description="Synthesises the final user-facing answer from specialist transcripts. Always called last.",
                agent_reference={"name": settings.response_agent_name, "type": "agent_reference"},
            )

            manager = Agent(
                client=client,
                name="manager",
                instructions=(
                    "You coordinate Pepsico specialist agents to answer an employee's question. "
                    "Plan the smallest set of specialist calls needed to answer fully. "
                    "Always finish by handing the consolidated context to `response_generator` "
                    "so the user sees a single, well-formatted reply."
                ),
            )

            workflow = MagenticBuilder(
                participants=[hr, products, marketing, response_generator],
                manager_agent=manager,
                max_round_count=8,
                max_stall_count=2,
                max_reset_count=1,
            ).build()

            result = OrchestratorResult(final_answer="")
            async for event in workflow.run(user_query, stream=True):
                etype = getattr(event, "type", "")
                if etype == "magentic_orchestrator":
                    data = getattr(event, "data", None)
                    if data is not None:
                        kind = getattr(getattr(data, "event_type", ""), "name", str(data))
                        result.events.append({"type": "manager", "kind": kind})
                        LOG.info("manager %s", kind)
                elif etype == "agent_response":
                    data = event.data
                    name = getattr(data, "agent_name", "?")
                    text = getattr(data, "text", "") or ""
                    result.transcripts[name] = text
                    result.plan.append(name)
                    if name == "response_generator":
                        result.final_answer = text
                elif etype == "output":
                    if not result.final_answer:
                        result.final_answer = getattr(event.data, "text", "")

            if not result.final_answer and result.transcripts:
                # Fallback if the manager forgot to call response_generator
                result.final_answer = next(reversed(result.transcripts.values()))

            return result

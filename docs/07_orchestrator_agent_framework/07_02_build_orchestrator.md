---
title: '2. Build the orchestrator'
layout: default
nav_order: 2
parent: 'Exercise 07: Magentic Orchestrator'
---

# Task 07.02 — Build the Magentic Orchestrator

## Introduction

You will implement `run_query` in `src/orchestrator/magentic_router.py`. It
opens a `FoundryChatClient` (from `agent_framework.foundry`) to drive the
manager, wraps each Foundry-hosted specialist as a `FoundryAgent`
participant, and runs the workflow with `MagenticBuilder`.

Note: the Response Generator agent does not exist yet — you create it in
Exercise 08. You can still wire it in here using `settings.response_agent_name`;
if it has not been created yet, the manager will simply not be able to call
it and you will fall back to the last transcript.

## Success Criteria

* `src/orchestrator/magentic_router.py` no longer raises `NotImplementedError`.
* `python -m src.orchestrator.runner --query "What is the PTO policy?"`
  produces a non-empty `final_answer`.

## Key Tasks

### 01: Implement `run_query`

Open [src/orchestrator/magentic_router.py](https://github.com/SinglaSandeep/ai-agents-workshop/blob/main/src/orchestrator/magentic_router.py).

<details markdown="block">
<summary><strong>Expand this section to view the solution</strong></summary>

```python
"""Magentic orchestrator that coordinates the Zava Foundry agents."""

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
    settings = get_settings()

    from agent_framework import Agent
    from agent_framework.foundry import FoundryAgent, FoundryChatClient
    from agent_framework.orchestrations import MagenticBuilder
    from azure.identity.aio import DefaultAzureCredential

    async with DefaultAzureCredential() as cred:
        # FoundryChatClient drives the (non-hosted) manager agent.
        # FoundryAgent(agent_name=...) references each hosted specialist
        # by name — its model + instructions + tools come from Foundry.
        async with FoundryChatClient(
            project_endpoint=settings.azure_ai_project_endpoint,
            model=settings.azure_ai_model_deployment,
            credential=cred,
        ) as client:
            hr = FoundryAgent(
                project_endpoint=settings.azure_ai_project_endpoint,
                agent_name=settings.store_ops_agent_name,
                credential=cred,
                name="hr",
                description="Answers Zava store-ops policy, benefits, and handbook questions using the Foundry IQ knowledge base.",
            )
            products = FoundryAgent(
                project_endpoint=settings.azure_ai_project_endpoint,
                agent_name=settings.products_agent_name,
                credential=cred,
                name="products",
                description="Answers questions about the Zava product catalog (SKU, brand, size, calories, price) using the Products MCP server.",
            )
            marketing = FoundryAgent(
                project_endpoint=settings.azure_ai_project_endpoint,
                agent_name=settings.marketing_agent_name,
                credential=cred,
                name="marketing",
                description="Answers questions about Zava marketing campaigns (status, KPIs, budgets, ROI) using the Marketing MCP server, and can search the web via Bing for live context.",
            )
            response_generator = FoundryAgent(
                project_endpoint=settings.azure_ai_project_endpoint,
                agent_name=settings.response_agent_name,
                credential=cred,
                name="response_generator",
                description="Synthesises the final user-facing answer from specialist transcripts. Always called last.",
            )

            manager = Agent(
                client=client, name="manager",
                instructions=(
                    "You coordinate Zava specialist agents to answer an employee's question. "
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
                result.final_answer = next(reversed(result.transcripts.values()))
            return result
```

</details>

### 02: Test from the CLI

```powershell
python -m src.orchestrator.runner --query "What is the PTO policy at Zava?"
```

You should see a printed plan like `hr -> response_generator` and a final
answer. If the Response Generator does not exist yet, you might see
`hr` only and the answer will be the raw HR transcript — that is OK for now.

## Next

Continue to [07.03 — Run the orchestrator from the chat UI](07_03_wire_orchestrator_into_chat.md).

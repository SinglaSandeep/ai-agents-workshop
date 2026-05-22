---
title: '3. Wire the agent into the chat UI'
layout: default
nav_order: 3
parent: 'Exercise 03: Products Foundry Agent'
---

# Task 03.03 — Wire the Products Agent Into the Chat UI

## Introduction

The chat app from Exercise 01 has an `AGENT_MODE` switch. When `AGENT_MODE=products`
it tries to call `run_single_agent("products", query)` — but that function
currently raises `NotImplementedError`.

In this task you fill in `run_single_agent`, flip the mode in `.env`, restart
uvicorn, and ask the Products agent real questions from the browser.

## Success Criteria

* `run_single_agent("products", "What Pepsi colas do you have?")` returns a
  string answer in a Python REPL.
* With `AGENT_MODE=products` in `.env`, the chat UI returns grounded answers
  that cite product ids.

## Key Tasks

### 01: Implement `run_single_agent`

Open [src/foundry_agents/run_single_agent.py](../../src/foundry_agents/run_single_agent.py).
The skeleton imports `get_settings` and explains the three steps in TODO
comments.

<details markdown="block">
<summary><strong>Expand this section to view the solution</strong></summary>

```python
"""Run a single Foundry agent and return its final text answer."""

from __future__ import annotations

from src.common.settings import get_settings


async def run_single_agent(mode: str, query: str) -> str:
    settings = get_settings()

    agent_name = {
        "products": settings.products_agent_name,
        "marketing": settings.marketing_agent_name,
        "hr": settings.hr_agent_name,
    }[mode]

    # Lazy import — only require agent-framework when this code runs.
    from agent_framework import Agent
    from agent_framework.azure import AzureAIAgentClient
    from azure.identity.aio import DefaultAzureCredential

    async with DefaultAzureCredential() as cred:
        async with AzureAIAgentClient(
            project_endpoint=settings.azure_ai_project_endpoint,
            model_deployment_name=settings.azure_ai_model_deployment,
            credential=cred,
        ) as client:
            agent = Agent(
                client=client,
                name=mode,
                agent_reference={"name": agent_name, "type": "agent_reference"},
            )
            response = await agent.run(query)
            return getattr(response, "text", str(response))
```

</details>

### 02: Wire it into `_dispatch`

Open [src/app/main.py](../../src/app/main.py). In `_dispatch`, replace the
`return _not_yet_wired(query, AGENT_MODE)` line inside the
`AGENT_MODE in {"products", "marketing", "hr"}` branch with the live call.

<details markdown="block">
<summary><strong>Expand this section to view the solution</strong></summary>

```python
    if AGENT_MODE in {"products", "marketing", "hr"}:
        from src.foundry_agents.run_single_agent import run_single_agent

        answer = await run_single_agent(AGENT_MODE, query)
        return {
            "final_answer": answer,
            "plan": [AGENT_MODE],
            "transcripts": {AGENT_MODE: answer},
            "events": [],
            "mode": AGENT_MODE,
        }
```

You can leave the `_not_yet_wired` helper in place — the orchestrator branch
still uses it until Exercise 07.

</details>

### 03: Flip `AGENT_MODE`

Edit `.env` and add (or change):

```
AGENT_MODE=products
```

Restart uvicorn (Ctrl+C, re-run `uvicorn src.app.main:app --reload --port 8000`).

### 04: Test in the browser

Open <http://127.0.0.1:8000> and try prompts like:

* *"What flavors of Lay's chips do you carry?"*
* *"Tell me about PEP-007."*
* *"Which beverages are under $5?"*

You should see grounded answers that include real product ids and prices from
Cosmos. The plan pill underneath should say `products`.

<details markdown="block">
<summary><strong>Expand this section if the agent answers from memory instead of calling the tool</strong></summary>

* Re-read the `INSTRUCTIONS` block in `create_products_agent.py`. It must say
  *"Only answer using data returned by the tools"*. If you altered it,
  re-run the script to push a new agent version.
* In the Foundry portal → Agents → your agent → **Playground**, test the same
  prompt. If you see *"Tool call required"* errors, the MCP connection's
  managed identity does not have `Invoker` rights on the Container App.

</details>

## Next

Continue to [Exercise 04 — Build & Deploy the Marketing MCP Server](../04_marketing_mcp_server/04_marketing_mcp_server.md).

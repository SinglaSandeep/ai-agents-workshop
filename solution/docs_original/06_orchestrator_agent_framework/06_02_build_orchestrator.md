---
title: '2. Walk through the orchestrator code'
layout: default
nav_order: 2
parent: 'Exercise 06: Magentic Orchestrator'
---

# Task 06.02 — Walk Through `magentic_router.py`

Open [`src/orchestrator/magentic_router.py`](../../src/orchestrator/magentic_router.py).

## Building the participants

Each specialist is a thin `Agent` that delegates to a **hosted Foundry agent**
by name. The participant doesn't *do* the work; it just hands the call off:

```python
hr = Agent(
    client=client,
    name="hr",
    description="Answers Pepsico HR policy, benefits, and handbook questions ...",
    agent_reference={"name": settings.hr_agent_name, "type": "agent_reference"},
)
```

The `description` is what the manager LLM sees when deciding who to call.
It is **the most important string in the whole orchestrator** — write it
well and the manager picks correctly.

## Building the manager

The manager is a regular Agent with planning instructions. It has no tools;
the framework gives it the participant catalog automatically.

```python
manager = Agent(
    client=client,
    name="manager",
    instructions=(
        "You coordinate Pepsico specialist agents to answer an employee's question. "
        "Plan the smallest set of specialist calls needed to answer fully. "
        "Always finish by handing the consolidated context to `response_generator`."
    ),
)
```

## Building the workflow

```python
workflow = MagenticBuilder(
    participants=[hr, products, marketing, response_generator],
    manager_agent=manager,
    max_round_count=8,
    max_stall_count=2,
    max_reset_count=1,
).build()
```

## Streaming the run

We iterate the streaming events to capture the plan + transcripts:

```python
async for event in workflow.run(user_query, stream=True):
    if event.type == "magentic_orchestrator":
        # ledger updates: PLAN_CREATED, PROGRESS_LEDGER_UPDATED, TASK_COMPLETED, ...
        ...
    elif event.type == "agent_response":
        name = event.data.agent_name
        text = event.data.text
        result.transcripts[name] = text
        if name == "response_generator":
            result.final_answer = text
```

The final answer is whatever the `response_generator` agent emits. As a
safety net, if the manager forgets to call the response generator we fall
back to the last specialist transcript.

## Success criteria

{: .success }
> - You can identify in the code (a) the participant wrappers, (b) the
>   manager, (c) the `MagenticBuilder` knobs, and (d) where the final answer
>   is captured

## Next

[06.03 — Run the orchestrator from the CLI](06_03_run_orchestrator.md).

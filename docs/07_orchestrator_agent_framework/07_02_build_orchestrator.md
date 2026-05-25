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
manager, wraps each Foundry specialist as a `FoundryAgent`
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


### 02: Test from the CLI

```powershell
python -m src.orchestrator.runner --query "What is the PTO policy at Zava?"
```

You should see a printed plan like `store_ops -> response_generator` and a final
answer. If the Response Generator does not exist yet, you might see
`store_ops` only and the answer will be the raw store-ops transcript — that is OK for now.

## Next

Continue to [07.03 — Run the orchestrator from the chat UI](07_03_wire_orchestrator_into_chat.md).

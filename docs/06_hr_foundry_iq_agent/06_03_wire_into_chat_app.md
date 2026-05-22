---
title: '3. Wire the agent into the chat UI'
layout: default
nav_order: 3
parent: 'Exercise 06: HR Foundry IQ Agent'
---

# Task 06.03 — Wire the HR Agent Into the Chat UI

## Introduction

Same drill as Exercises 03 and 05: `run_single_agent` already dispatches by
mode, so all you need to do is flip `AGENT_MODE`.

## Success Criteria

* With `AGENT_MODE=hr`, the chat UI returns grounded HR answers ending with a
  `Sources:` line.

## Key Tasks

### 01: Flip the mode

```
AGENT_MODE=hr
```

Restart uvicorn.

### 02: Test in the browser

| Prompt | Expected |
| ------ | -------- |
| *"What is Pepsico's PTO policy?"* | Cites `pepsico_pto_policy.md` |
| *"What benefits does Pepsico offer?"* | Cites `pepsico_benefits_summary.md` |
| *"How many SKUs does Pepsi Cola have?"* | Politely declines — agent only knows HR. |

You now have three working specialist agents, each individually usable from
the chat UI. The next exercise stitches them together so the user can ask a
single mixed question.

## Next

Continue to [Exercise 07 — Build the Magentic Orchestrator](../07_orchestrator_agent_framework/07_orchestrator_agent_framework.md).

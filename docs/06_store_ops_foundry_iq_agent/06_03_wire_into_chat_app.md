---
title: '3. Talk to the Store Ops agent in DevUI'
layout: default
nav_order: 3
parent: 'Exercise 06: Store-Ops Foundry IQ Agent'
---

# Task 06.03 — Talk to the Store Ops Agent in DevUI

## Introduction

The DevUI launcher already references the Store Ops agent by name
(`STORE_OPS_AGENT_NAME=zava-store-ops-agent`), so all you need to do is restart it.

## Success Criteria

* In DevUI, the **store_ops** agent returns grounded answers ending with a
  `Sources:` line.

## Key Tasks

### 01: Restart DevUI

```powershell
python -m src.app.devui_launch
```

### 02: Test in the browser

Pick the **store_ops** agent from the sidebar at <http://127.0.0.1:8080>.

| Prompt | Expected |
| ------ | -------- |
| *"What is Zava's PTO policy?"* | Cites `pto_and_scheduling.md` |
| *"What benefits does Zava offer?"* | Cites `employee_onboarding.md` |
| *"How many SKUs does the Premium Interior Paint have?"* | Politely declines — agent only knows store-ops content (handbooks, returns, safety, HR, SOPs). |

You now have three working specialist agents, each individually usable from
DevUI. The next exercise stitches them together so the user can ask a
single mixed question.

## Next

Continue to [Exercise 07 — Build the Magentic Orchestrator](../07_orchestrator_agent_framework/07_orchestrator_agent_framework.md).

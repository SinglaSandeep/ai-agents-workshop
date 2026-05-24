---
title: '3. Talk to the HR agent in DevUI'
layout: default
nav_order: 3
parent: 'Exercise 06: HR Foundry IQ Agent'
---

# Task 06.03 — Talk to the HR Agent in DevUI

## Introduction

The DevUI launcher already references the HR agent by name
(`HR_AGENT_NAME=pepsico-hr-agent`), so all you need to do is restart it.

## Success Criteria

* In DevUI, the **hr** agent returns grounded HR answers ending with a
  `Sources:` line.

## Key Tasks

### 01: Restart DevUI

```powershell
python -m src.app.devui_launch
```

### 02: Test in the browser

Pick the **hr** agent from the sidebar at <http://127.0.0.1:8080>.

| Prompt | Expected |
| ------ | -------- |
| *"What is Pepsico's PTO policy?"* | Cites `pepsico_pto_policy.md` |
| *"What benefits does Pepsico offer?"* | Cites `pepsico_benefits_summary.md` |
| *"How many SKUs does Pepsi Cola have?"* | Politely declines — agent only knows HR. |

You now have three working specialist agents, each individually usable from
DevUI. The next exercise stitches them together so the user can ask a
single mixed question.

## Next

Continue to [Exercise 07 — Build the Magentic Orchestrator](../07_orchestrator_agent_framework/07_orchestrator_agent_framework.md).

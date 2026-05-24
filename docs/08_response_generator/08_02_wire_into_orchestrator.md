---
title: '2. Verify the orchestrator hand-off'
layout: default
nav_order: 2
parent: 'Exercise 08: Response Generator'
---

# Task 08.02 — Verify the Orchestrator Hand-Off

## Introduction

The Magentic orchestrator from Exercise 07 already calls the Response
Generator as its final step (see `src/orchestrator/`). Once the agent exists
in Foundry, the orchestrator will pick it up automatically.

## Success Criteria

* Running `python -m src.orchestrator.runner` for a multi-specialist
  question ends with a single polished message whose plan includes
  `response_generator` as the last step.

## Key Tasks

### 01: Run the orchestrator

```powershell
python -m src.orchestrator.runner --query "How does our 2026 SuperBowl Gatorade push compare to our latest hydration product launch, and what HR support is available for the marketing team during launch week?"
```

Expected:

* The **Plan** line shows `marketing -> products -> hr -> response_generator`.
* The final reply is the polished single message produced by the Response
  Generator and includes a `Sources:` line.

## Next

Continue to [Exercise 09 — Evaluations](../09_evaluations/09_evaluations.md).

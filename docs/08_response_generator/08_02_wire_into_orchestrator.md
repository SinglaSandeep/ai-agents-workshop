---
title: '2. Verify the orchestrator hand-off'
layout: default
nav_order: 2
parent: 'Exercise 08: Response Generator'
---

# Task 08.02 — Verify the Orchestrator Hand-Off

## Introduction

The Magentic orchestrator from Exercise 07 already calls the Response
Generator as its final step. Once the agent exists in Foundry, the
orchestrator will pick it up automatically.

## Success Criteria

* Asking a multi-specialist question in the **web UI** (or the CLI) ends
  with a single polished message whose plan includes `response_generator`
  as the last step.

## Key Tasks

### 01: Re-open the orchestrator web UI

If it is not already running, start it from the workshop root:

```powershell
uvicorn src.app.main:app --reload --port 8000
```

Then open <http://127.0.0.1:8000>.

### 02: Ask a multi-specialist question

In the chat panel, ask:

> *How does our 2026 Spring Paint Sale push compare to our latest power-tool
> product launch, and what HR support is available for the marketing team
> during launch week?*

You should see:

* the **Marketing**, **Products**, and **Store Ops** boxes light up in turn,
* the **Response** box turns green last,
* the chat panel shows one polished reply (typically ending with a
  `Sources:` line).

### 03: Optional — verify from the CLI

```powershell
python -m src.orchestrator.runner --query "How does our 2026 Spring Paint Sale push compare to our latest power-tool product launch, and what HR support is available for the marketing team during launch week?"
```

The printed **Plan** line should end in `... -> response_generator`.

## Next

Continue to [Exercise 09 — Evaluations](../09_evaluations/09_evaluations.md).

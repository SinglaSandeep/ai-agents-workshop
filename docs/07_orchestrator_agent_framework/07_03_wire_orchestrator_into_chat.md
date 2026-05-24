---
title: '3. Run the orchestrator'
layout: default
nav_order: 3
parent: 'Exercise 07: Magentic Orchestrator'
---

# Task 07.03 — Run the Magentic Orchestrator

## Introduction

The orchestrator runs as a small Python CLI that calls `run_query` from
`src/orchestrator/magentic_router.py`. There is nothing else to wire up — the
specialists are already discovered by name from your Foundry project.

## Success Criteria

* `python -m src.orchestrator.runner --query "..."` prints a multi-step plan
  and a final answer for a mixed-domain question.

## Key Tasks

### 01: Run the orchestrator from the terminal

From the workshop root, with `.venv` activated and `.env` populated:

```powershell
python -m src.orchestrator.runner --query "Which active Gatorade campaigns target youth athletes, and what is the PTO policy for marketing managers attending those activations?"
```

You should see output like:

```
=== Plan ===
marketing -> hr -> response_generator

=== Final Answer ===
Gatorade is currently running ...
```

### 02: Inspect the full result (optional)

Pass `--json` to dump the plan, specialist transcripts, and raw events:

```powershell
python -m src.orchestrator.runner --query "What is our PTO policy?" --json
```

### 03: Try mixed-domain prompts

Good questions to exercise the planner:

* *"List two Pepsi Zero Sugar SKUs and tell me the parental leave policy."*
* *"Which marketing campaigns mention 'youth athletes', and what training is
  required before staffing one of those activations?"*

If the **Final Answer** looks like a raw HR transcript, the Response
Generator agent does not exist yet — Exercise 08 fixes that.

## Next

Continue to [Exercise 08 — Response Generator](../08_response_generator/08_response_generator.md).

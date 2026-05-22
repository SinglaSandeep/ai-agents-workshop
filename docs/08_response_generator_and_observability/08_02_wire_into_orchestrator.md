---
title: '2. Verify the orchestrator hand-off'
layout: default
nav_order: 2
parent: 'Exercise 08: Response Generator + Observability'
---

# Task 08.02 — Verify the Orchestrator Hand-off

## Introduction

The orchestrator already lists `response_generator` as the last participant
(you wrote that in Exercise 07). With the agent now created, the manager will
actually be able to call it and you should see polished final answers.

## Success Criteria

* The chat UI plan now ends with `response_generator`.
* The `final_answer` follows the rules in the Response Generator prompt
  (single direct sentence, then 1-3 paragraphs, then `Sources:` line).

## Key Tasks

### 01: Re-run a mixed prompt

With `AGENT_MODE=orchestrator` still in `.env`, ask:

> *"Which active Gatorade campaigns target youth athletes, and what is the
> PTO policy for marketing managers attending those activations?"*

Confirm:

* Plan pills include `response_generator` at the end.
* The final answer has the expected shape and a `Sources:` line.

### 02: Inspect the transcripts

Expand the **Specialist transcripts** disclosure. You should see one entry per
participant the manager actually called.

If `response_generator` is missing, check the Foundry portal that the agent
exists at the exact name in `RESPONSE_AGENT_NAME`.

## Next

Continue to [08.03 — Enable observability](08_03_observability.md).

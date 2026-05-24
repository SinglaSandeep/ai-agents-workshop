---
title: 'Exercise 08: Response Generator'
layout: default
nav_order: 10
has_children: true
---

# Exercise 08 — Add the Response Generator Agent

## Scenario

A dedicated **Response Generator** agent turns the raw specialist transcripts
produced by the Magentic orchestrator into one polished Pepsico-voice reply
with citations. Keeping synthesis separate from the specialists keeps each
agent simple and the final UX consistent.

## Description

You will:

1. Implement and create the `pepsico-response-generator` Foundry Prompt Agent
   (no tools — it is a pure synthesiser).
2. Confirm the orchestrator hands off to it as the last step.

## Success Criteria

{: .success }
> - `python -m src.foundry_agents.create_response_agent` succeeds.
> - Running the orchestrator (`python -m src.orchestrator.runner --query "..."`)
>   ends with a single direct sentence + supporting paragraphs ending in a
>   `Sources:` line, and the plan includes `response_generator` as the last
>   step.

## Tasks

| Task | Description |
| ---- | ----------- |
| [08.01 — Create the Response Generator agent](08_01_create_response_agent.md) | Implement `create_response_agent.py`. |
| [08.02 — Verify the orchestrator hand-off](08_02_wire_into_orchestrator.md) | Re-run `src.orchestrator.runner` and confirm `response_generator` is in the plan. |

> Observability, Evaluations, Guardrails and Red Teaming are covered in the
> later modules (09, 10, 11) so that you can layer them on top of a working
> multi-agent system rather than mid-way through building it.

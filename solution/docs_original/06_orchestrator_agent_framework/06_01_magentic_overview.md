---
title: '1. Magentic orchestration overview'
layout: default
nav_order: 1
parent: 'Exercise 06: Magentic Orchestrator'
---

# Task 06.01 — Magentic Orchestration Concepts

Magentic (from
[Magentic-One](https://github.com/microsoft/autogen/tree/main/python/packages/autogen-magentic-one))
is a planning pattern implemented in the Microsoft Agent Framework as
`MagenticBuilder`. The core ideas:

| Concept | What it does |
| ------- | ------------ |
| **Participants** | The set of specialist agents the manager can call. Each is described by its `name` + `description` so the manager can pick. |
| **Manager agent** | A planner LLM agent. It maintains an internal **progress ledger** and decides which participant to call next, or that the task is done. |
| **Progress ledger** | The manager's running summary of what's been learned and what's still open. Updated after every participant turn. |
| **Termination** | The manager stops when (a) the ledger shows the task is complete, (b) `max_round_count` is reached, (c) `max_stall_count` consecutive turns make no progress. |
| **Streaming events** | `magentic_orchestrator` events expose ledger updates; `agent_response` events expose participant outputs. |

## Why these knobs matter

- **`max_round_count=8`** — bounds the worst-case cost. For Pepsico
  cross-domain queries 4-6 rounds is typical.
- **`max_stall_count=2`** — if the manager fails to make progress for 2
  rounds, the workflow ends rather than spinning forever.
- **`max_reset_count=1`** — allow one full replan if the first attempt got stuck.

## How our orchestrator is wired

We register **four participants**:

| name | role |
| ---- | ---- |
| `hr` | The Foundry HR agent (Exercise 03) |
| `products` | The Foundry Products agent (Exercise 04) |
| `marketing` | The Foundry Marketing agent (Exercise 05) |
| `response_generator` | The Foundry Response Generator (Exercise 07) |

The manager agent gets instructions:

> *Plan the smallest set of specialist calls needed to answer fully. Always
> finish by handing the consolidated context to `response_generator`.*

The wrapper exposes the four Foundry agents to the framework via
`Agent(agent_reference={"name": "...", "type": "agent_reference"})`. The
framework then routes `.run()` calls through the Foundry Responses API — we
get all the planning machinery **without** running the specialists locally.

## Success criteria

{: .success }
> - You can describe what a participant, manager, and progress ledger are
> - You can explain why we include `response_generator` as a participant
>   rather than hard-coding it at the end

## Next

[06.02 — Walk through the orchestrator code](06_02_build_orchestrator.md).

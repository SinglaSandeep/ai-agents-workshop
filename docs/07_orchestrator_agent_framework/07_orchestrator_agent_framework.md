---
title: 'Exercise 07: Magentic Orchestrator'
layout: default
nav_order: 9
has_children: true
---

# Exercise 07 — Build the Magentic Multi-Agent Orchestrator

## Scenario

Each specialist works in isolation, but real Zava questions often cross
domains: *"Which active power-tool campaigns are running this quarter, and what is
the PTO policy for marketing managers attending those activations?"* A single
agent cannot answer that — the orchestrator can.

You will build a **Magentic** orchestrator with the **Microsoft Agent
Framework**. Magentic uses a small **manager** model to plan a sequence of
calls across the three specialists, then synthesises a final answer.

## Description

You will:

1. Read a short overview of how Magentic plans and stalls.
2. Fill in `src/orchestrator/magentic_router.py` so it wraps the three
   specialist Foundry agents and a manager.
3. Run mixed-domain queries through `python -m src.orchestrator.runner`.

## Architecture

```mermaid
flowchart LR
    U[User / CLI] --> M[Magentic Manager]
    M --> SO[Store Ops Agent (Foundry IQ)]
    M --> PR[Products Agent (MCP)]
    M --> MK[Marketing Agent (MCP + Bing)]
    M --> RG[Response Generator (Ex 08)]
```

## Success Criteria

{: .success }
> - `src/orchestrator/magentic_router.py` no longer raises `NotImplementedError`.
> - `python -m src.orchestrator.runner --query "What is our PTO policy?"`
>   returns a real answer.
> - A mixed-domain question yields a plan with multiple specialists (e.g.
>   `marketing → store_ops → response_generator`).

## Learning Resources

* [Microsoft Agent Framework — Magentic](https://learn.microsoft.com/azure/ai-foundry/agents/agent-framework-magentic)
* [Magentic-One paper (background)](https://arxiv.org/abs/2411.04468)

## Tasks

| Task | Description |
| ---- | ----------- |
| [07.01 — Magentic in 5 minutes](07_01_magentic_overview.md) | The mental model: manager, participants, plan, stall, reset. |
| [07.02 — Build the orchestrator](07_02_build_orchestrator.md) | Implement `run_query` in `magentic_router.py`. |
| [07.03 — Run the orchestrator in the web UI](07_03_wire_orchestrator_into_chat.md) | Start the Zava chat app and watch the workflow run live in the browser. |

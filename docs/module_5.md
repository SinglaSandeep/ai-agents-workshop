---
title: 'Module 5: Orchestrate & Deploy'
layout: default
nav_order: 8
has_children: true
---

# Module 5 — Orchestrate & Deploy

**Goal:** Understand why naïve multi-agent systems break, then orchestrate the
specialist agents reliably with the **Magentic** pattern (an LLM manager plans
the route) — adding the **Action Recommender** and **Response Generator** — and
finally **deploy** the complete chat app to Azure.

## Multi-agent challenges → how they're overcome

| Challenge | What goes wrong | How it's overcome |
| --------- | --------------- | ----------------- |
| Orchestration & routing | Agent-to-agent webs loop or hand off to the wrong agent | Magentic manager plans and delegates via a shared task ledger |
| Context bloat | Full context to every agent → token explosion | Scoped context per agent; Response Generator composes the final answer |
| Non-determinism | Same input → different paths, hard to reproduce | Orchestrator planning + evaluations (Module 6) |
| Cost & latency | Many agents × many calls = runaway spend | Token/cost observability; right-size the model per agent |
| Error propagation | One bad agent poisons downstream agents | Isolated hosted agents; Action agent validates before the final reply |
| Tool sprawl | Every agent re-implements the same tools | Shared, reusable MCP servers across agents |
| Observability gaps | Can't see why an answer was produced | Distributed tracing (Module 6) |

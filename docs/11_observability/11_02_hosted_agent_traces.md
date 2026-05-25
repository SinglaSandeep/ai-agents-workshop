---
title: '2. Foundry agent traces'
layout: default
nav_order: 2
parent: 'Exercise 11: Observability'
---

# Task 11.02 — Foundry Agent Traces

## Introduction

Every Foundry Prompt Agent (Products, Marketing, Store-Ops, Response) emits
**server-side traces** automatically — model calls, tool calls (including
MCP tools and the Code Interpreter), token counts, latency. You don't
configure anything on the agent itself; everything is in the Foundry portal.

## Success Criteria

* `zava-marketing-agent` shows trace activity in the Foundry portal under
  **Agents → zava-marketing-agent → Observability**.
* You can drill from a chat-app trace in App Insights into the matching
  agent run in Foundry.

## Key Tasks

### 01: View agent traces in Foundry

Foundry portal → **Agents → zava-marketing-agent → Observability** →
filter on the last hour. Expand a trace to see the model call and each
tool call (Marketing MCP, Code Interpreter, Marketing KB MCP).

Repeat for the other agents — `zava-products-agent`,
`zava-store-ops-agent`, `zava-response-agent`.

### 02: Filter by `agent_run_id`

Each trace surfaces an `agent_run_id`. The chat app logs it when the
orchestrator calls the agent, so you can paste an ID from App Insights into
the Foundry trace search and jump straight to that run.

### 03: Correlate chat-app and agent traces

The chat app sends an `traceparent` HTTP header on every Foundry call. In
App Insights, open a `zava.chat` operation and follow the `operation_Id` —
the matching agent runs show up linked under the same operation.

## Next

Continue to [11.03 — KQL queries you'll actually use](11_03_kql_queries.md).

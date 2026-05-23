---
title: '2. Hosted-agent traces'
layout: default
nav_order: 2
parent: 'Exercise 11: Observability'
---

# Task 11.02 — Hosted-Agent Traces

## Introduction

Foundry automatically injects `APPLICATIONINSIGHTS_CONNECTION_STRING` into the
hosted-agent container at runtime. Our `marketing_hosted/main.py` already
calls `enable_instrumentation()` so the agent emits OpenTelemetry traces for
every chat call and every MCP tool invocation.

## Success Criteria

* `pepsico-marketing-agent` shows trace activity in Foundry portal under
  **Agents → pepsico-marketing-agent → Observability**.
* `azd ai agent monitor -f` streams logs in real time.

## Key Tasks

### 01: View hosted-agent traces in Foundry

Foundry portal → **Agents → pepsico-marketing-agent → Observability** →
filter on the last hour. Expand a trace to see the model call, the three
MCP tool calls, and any content-filter middleware events.

### 02: Stream logs with azd

```powershell
azd ai agent monitor -f
```

You'll see one stdout line per request along with any logger output the
agent emits (e.g. `logger.info("Using KB MCP at %s", kb_url)`).

### 03: Correlate chat-app and hosted-agent traces

The chat app sends an `traceparent` HTTP header on every Foundry call. In
App Insights, click into a `pepsico.chat` operation and follow the
`operation_Id` — you'll see the matching hosted-agent spans collected from
the marketing-agent container.

## Next

Continue to [11.03 — KQL queries you'll actually use](11_03_kql_queries.md).

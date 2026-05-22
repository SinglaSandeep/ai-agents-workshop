---
title: '3. Enable observability'
layout: default
nav_order: 3
parent: 'Exercise 08: Response Generator + Observability'
---

# Task 08.03 — Enable Observability

## Introduction

`src/common/observability.py` is already wired into `main.py`. It is a no-op
unless `APPLICATIONINSIGHTS_CONNECTION_STRING` is set. Once it is, the
FastAPI app, all HTTPX calls (which is how the Foundry SDK reaches Azure),
and any manual `trace_span(...)` blocks all emit spans to Application
Insights and to Foundry tracing.

## Success Criteria

* `GET /health` returns `"observability_enabled": true`.
* Spans named `pepsico.chat` appear in App Insights → Transaction search.

## Key Tasks

### 01: Set the connection string

In `.env`:

```
APPLICATIONINSIGHTS_CONNECTION_STRING=InstrumentationKey=...;IngestionEndpoint=...
```

Restart uvicorn. Confirm `/health` now reports `observability_enabled: true`.

### 02: Issue some chats

Run a few prompts through the chat UI. Within a minute or two:

1. Open Application Insights for your workshop subscription.
2. **Investigate → Transaction search → Event types: Request, Dependency, Trace**.
3. Filter by `pepsico.chat`. You should see one event per chat call and child
   dependency spans for each Foundry / Cosmos call.

### 03: View the trace in Foundry

Open the Foundry portal → your project → **Observability → Traces** and filter
by your project. The same trace tree is visible there with per-agent spans.

## Success

You now have:

* A runnable Pepsico chat UI.
* Three specialist Foundry agents (HR, Products, Marketing) reachable
  individually via `AGENT_MODE`.
* A Magentic orchestrator that plans across them.
* A Response Generator producing the final answer.
* End-to-end OpenTelemetry tracing.

## Next

Continue to [Exercise 09 — Resource Cleanup](../09_cleanup/09_cleanup.md).

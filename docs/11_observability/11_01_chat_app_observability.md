---
title: '1. Chat-app observability'
layout: default
nav_order: 1
parent: 'Exercise 11: Observability'
---

# Task 11.01 — Enable Chat-App Observability

## Introduction

`src/common/observability.py` is a no-op unless
`APPLICATIONINSIGHTS_CONNECTION_STRING` is set. Once it is, the FastAPI app,
all HTTPX calls (which is how the Foundry SDK reaches Azure), and any manual
`trace_span(...)` blocks emit spans to Application Insights and to Foundry
tracing.

## Success Criteria

* `GET /health` returns `"observability_enabled": true`.
* Spans named `zava.chat` appear in App Insights → Transaction search.

## Key Tasks

### 01: Set the connection string

In `.env`:

```
APPLICATIONINSIGHTS_CONNECTION_STRING=InstrumentationKey=...;IngestionEndpoint=...
```

Restart uvicorn and confirm `/health` reports `observability_enabled: true`.

### 02: Issue some chats

Run a few prompts through the chat UI. Within a minute or two open Application
Insights → **Investigate → Transaction search** and filter by `zava.chat`.
You should see one event per chat call and child dependency spans for each
Foundry / Cosmos call.

## Next

Continue to [11.02 — Hosted-agent traces](11_02_hosted_agent_traces.md).

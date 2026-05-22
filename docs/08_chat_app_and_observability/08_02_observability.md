---
title: '2. Add observability'
layout: default
nav_order: 2
parent: 'Exercise 08: Chat App & Observability'
---

# Task 08.02 — Add OpenTelemetry → Application Insights / Foundry Tracing

The app already calls `configure_observability(app)` in
[`src/common/observability.py`](../../src/common/observability.py). It's a
**no-op** until two things are true:

1. The optional `observability` extras are installed.
2. `APPLICATIONINSIGHTS_CONNECTION_STRING` is set in `.env`.

When both are true, every `POST /chat` becomes a distributed trace that
spans FastAPI, the Magentic workflow, and the Foundry agent calls. Foundry's
own **Tracing** experience picks up the same traces because it reads from
the same App Insights workspace.

## Steps

1. **Install the observability extras**

   ```powershell
   python -m pip install -e ".[observability]"
   ```

2. **Set the connection string in `.env`**

   ```powershell
   "APPLICATIONINSIGHTS_CONNECTION_STRING=$(az monitor app-insights component show -g $env:AZURE_RESOURCE_GROUP -a <appi-name> --query connectionString -o tsv)"
   ```

   Paste the printed line into `.env`.

3. **Restart the app**

   ```powershell
   uvicorn src.app.main:app --reload --port 8000
   ```

   `GET /health` should now report `"observability_enabled": true`.

4. **Issue 3-5 chat requests through the UI**

5. **View the traces in App Insights**

   Portal → Application Insights → **Investigate → Transaction search**.
   Filter on `service.name = pepsico-agents-workshop`. Click any request to
   see the full distributed trace.

6. **View the same traces in Foundry**

   Foundry portal → your project → **Observability → Tracing**. Each chat
   request shows up with manager rounds, participant calls, and tool
   invocations as nested spans.

## What's instrumented

| Layer | Spans you'll see |
| ----- | ---------------- |
| FastAPI | `POST /chat` (HTTP server span) |
| Chat handler | `pepsico.chat` (custom span with the user query) |
| Magentic orchestrator | `magentic.run`, one span per manager round |
| Foundry agent runs | OpenAI Responses API spans (via `azure-monitor-opentelemetry` auto-instrumentation) |
| HTTP egress | `azure-cosmos`, MCP `httpx` calls |

## Privacy note

By default the user `query` is captured as a span attribute. If your data
classification forbids that, remove it from the `trace_span` call in
`src/app/main.py`.

## Success criteria

{: .success }
> - `GET /health` reports `observability_enabled: true`
> - A `/chat` request appears in App Insights → Transaction search as a
>   single end-to-end trace with at least 4 child spans
> - The same trace is visible in **Foundry → Observability → Tracing**

## Next

[Exercise 09 — Resource Cleanup](../09_cleanup/09_cleanup.md).

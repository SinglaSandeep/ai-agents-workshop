---
title: 'Exercise 05: Add Observability for Microsoft Foundry'
layout: default
nav_order: 6
parent: Workshop Guide
---

# Exercise 05: Add Observability for Microsoft Foundry

## Goal

Instrument the local multi-agent app so agent calls can produce telemetry. The app continues to run without Azure, but when an Application Insights connection string is provided it exports traces that can be reviewed with Azure Monitor and Microsoft Foundry observability workflows.

## What You Build

- Optional Application Insights export through `azure-monitor-opentelemetry`
- FastAPI instrumentation for `/chat`, `/agents`, and `/health`
- Custom spans for CLI and API agent calls
- A repeatable traffic generation checklist for reviewing traces

## Steps

1. Install the optional observability dependencies.

```bash
python -m pip install -e ".[observability]"
```

2. Create a local `.env` file.

```powershell
copy .env.sample .env
```

3. Add your Application Insights connection string to `.env`.

```text
APPLICATIONINSIGHTS_CONNECTION_STRING=InstrumentationKey=...;IngestionEndpoint=...
```

4. Start the web app.

```bash
uvicorn app.main:app --reload --port 8000
```

5. Confirm observability is enabled.

```bash
curl http://127.0.0.1:8000/health
```

Expected result:

```json
{"status":"ok","observability_enabled":true}
```

6. Generate traffic for each route.

```bash
python -m app.cli --query "What is the PTO policy?"
python -m app.cli --query "How much is the fitness watch?"
python -m app.cli --query "What is our brand voice?"
```

7. Generate API traffic from the browser UI at http://127.0.0.1:8000.

8. Review telemetry in Application Insights.

Open the Application Insights resource connected to your environment and review:

- Transaction search
- Request count and latency
- Failures
- Dependencies
- Traces with span names such as `api.agent_query` and `cli.agent_query`

9. Review Foundry observability concepts.

When this local app is later connected to Foundry agents or FoundryIQ knowledge bases, use the same observability workflow from the original workshop:

- Enable monitoring in Microsoft Foundry.
- Connect Application Insights to the Foundry project.
- Review the Monitor dashboard for requests, latency, token usage, and failures.
- Review Traces for agent calls and tool operations.

## Success Criteria

- The app still runs locally without an Application Insights connection string.
- `/health` returns `observability_enabled: true` after you install optional dependencies and set the connection string.
- CLI and API calls create custom spans named `cli.agent_query` or `api.agent_query`.
- You can filter telemetry by route attributes such as `agent=hr`, `agent=products`, or `agent=marketing`.
- You can describe how the same traces would support Foundry Monitor and Tracing review once the local agents are replaced with Foundry-hosted agents or FoundryIQ knowledge bases.

## Running Version

The app now runs locally with optional cloud telemetry export:

```bash
uvicorn app.main:app --reload --port 8000
```

Open http://127.0.0.1:8000, ask questions across all three domains, and inspect the emitted traces.

## Troubleshooting

| Issue | Fix |
| --- | --- |
| `observability_enabled` is false | Confirm `.env` contains `APPLICATIONINSIGHTS_CONNECTION_STRING` and the optional dependencies are installed. |
| No traces appear | Wait a few minutes, generate fresh traffic, and check that the connection string points to the expected Application Insights resource. |
| Local app fails after enabling observability | Remove the connection string to verify the app still runs, then reinstall the optional dependencies. |

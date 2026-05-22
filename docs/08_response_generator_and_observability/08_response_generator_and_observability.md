---
title: 'Exercise 08: Response Generator + Observability'
layout: default
nav_order: 10
has_children: true
---

# Exercise 08 — Add the Response Generator + Observability

## Scenario

Two things polish the assistant to a production-ready feel:

1. A dedicated **Response Generator** agent that turns raw specialist
   transcripts into one Pepsico-voice answer with citations.
2. **OpenTelemetry + Application Insights** so every chat round is searchable
   in App Insights and Foundry tracing.

## Description

You will:

1. Implement and create the `pepsico-response-generator` Foundry agent
   (no tools — it is a pure synthesiser).
2. Confirm the orchestrator hands off to it last.
3. Set `APPLICATIONINSIGHTS_CONNECTION_STRING` and watch traces light up.

## Success Criteria

{: .success }
> - `python -m src.foundry_agents.create_response_agent` succeeds.
> - In the chat UI (`AGENT_MODE=orchestrator`), the **Final Answer** is a
>   single direct sentence + supporting paragraphs ending in a `Sources:` line.
> - `GET /health` returns `"observability_enabled": true`.
> - Traces for `pepsico.chat` show up in App Insights under
>   **Investigate → Transaction search**.

## Learning Resources

* [Azure Monitor OpenTelemetry distro](https://learn.microsoft.com/azure/azure-monitor/app/opentelemetry-enable)
* [Foundry tracing for agents](https://learn.microsoft.com/azure/ai-foundry/observability/tracing)

## Tasks

| Task | Description |
| ---- | ----------- |
| [08.01 — Create the Response Generator agent](08_01_create_response_agent.md) | Implement `create_response_agent.py`. |
| [08.02 — Verify the orchestrator hand-off](08_02_wire_into_orchestrator.md) | Re-run with `AGENT_MODE=orchestrator` and confirm `response_generator` is in the plan. |
| [08.03 — Enable observability](08_03_observability.md) | Set the App Insights connection string and view traces. |

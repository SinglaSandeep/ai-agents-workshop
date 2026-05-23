---
title: 'Exercise 11: Observability'
layout: default
nav_order: 13
has_children: true
---

# Exercise 11 — Observability End-to-End

## Scenario

Now that the multi-agent system is wired, hosted, evaluated, and guard-railed,
the final operational layer is **observability**. We'll turn on tracing from
both the chat app and the hosted agent so every request — orchestrator plan,
each specialist call, each MCP tool call — flows into **Application Insights**
and the **Foundry observability** panel.

## Description

You will:

1. Set `APPLICATIONINSIGHTS_CONNECTION_STRING` and confirm
   `src/common/observability.py` turns on OTel exporters for the chat app.
2. Confirm the hosted Marketing agent emits its own traces (Foundry injects
   the connection string into the container automatically).
3. Query traces in **App Insights** and in **Foundry → Observability → Traces**.

## Success Criteria

{: .success }
> - `GET /health` reports `"observability_enabled": true`.
> - `pepsico.chat` spans appear in App Insights with child spans for each
>   specialist call.
> - The hosted Marketing agent shows traces in Foundry portal under
>   **Agents → pepsico-marketing-agent → Observability**.
> - `azd ai agent monitor -f` streams live logs.

## Learning Resources

* [Azure Monitor OpenTelemetry distro](https://learn.microsoft.com/azure/azure-monitor/app/opentelemetry-enable)
* [Foundry tracing for agents](https://learn.microsoft.com/azure/ai-foundry/observability/tracing)
* [Microsoft Agent Framework observability](https://learn.microsoft.com/agent-framework/agents/observability)

## Tasks

| Task | Description |
| ---- | ----------- |
| [11.01 — Enable chat-app observability](11_01_chat_app_observability.md) | Turn on App Insights for the chat app. |
| [11.02 — Hosted-agent traces](11_02_hosted_agent_traces.md) | View hosted-agent traces in Foundry and stream `azd ai agent monitor`. |
| [11.03 — KQL queries you'll actually use](11_03_kql_queries.md) | Useful queries for tool calls, latency and errors. |

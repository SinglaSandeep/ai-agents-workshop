---
title: 'Exercise 05: Marketing Hosted Agent (Foundry IQ + Web Tool)'
layout: default
nav_order: 7
has_children: true
---

# Exercise 05 — Build a Foundry-Hosted Marketing Agent (Foundry IQ + Web Tool)

## Scenario

The Marketing team wants a specialist that:

1. Reaches authoritative Zava campaign data (the Marketing MCP server from
   Exercise 04 plus a Foundry IQ knowledge base of marketing briefs and
   one-pagers).
2. Can pull in **live web context** (industry news, competitor announcements).
3. Runs **inside Microsoft Foundry as a hosted agent** — so the Foundry
   platform manages scaling, identity, tracing, content safety, and
   evaluations for us.

We will build the Marketing agent on the **Microsoft Agent Framework** using
the `agent_framework_foundry_hosting.ResponsesHostServer` pattern and deploy
it with `azd ai agent up`. The agent will reach Foundry built-in tools
(`web_search`, `code_interpreter`) through the **Foundry Toolbox** MCP endpoint
and an **Azure AI Search Knowledge Base** through its KB MCP endpoint
(Foundry IQ).

> Inspired by
> [Azure-Samples/foundry-hosted-agentframework-demos](https://github.com/Azure-Samples/foundry-hosted-agentframework-demos).

## Description

You will:

1. Seed a **Foundry IQ knowledge base** of marketing briefs alongside the
   existing Marketing MCP server.
2. Implement `src/foundry_agents/marketing_hosted/main.py` — a Microsoft Agent
   Framework agent that wires three tools:
   - `MCPStreamableHTTPTool` → Marketing MCP server (Cosmos truth).
   - `MCPStreamableHTTPTool` → Foundry Toolbox (`web_search`, `code_interpreter`).
   - `MCPStreamableHTTPTool` → Marketing Foundry IQ KB
     (`knowledge_base_retrieve`).
3. Run the agent locally with `azd ai agent run` and invoke it with
   `azd ai agent invoke --local`.
4. Deploy it to Foundry hosted agents with `azd ai agent up`.
5. Talk to the hosted agent in the **Agent Framework DevUI** and confirm
   the orchestrator routes campaign questions to it.

## Success Criteria

{: .success }
> - `zava-marketing-kb` Foundry IQ knowledge base exists and contains the
>   seeded marketing briefs.
> - `azd ai agent run` brings up the agent locally on
>   `http://localhost:8088/responses`.
> - `azd ai agent invoke --local "What is the ROI of CMP-2026-001?"` returns
>   data from the Marketing MCP server.
> - `azd ai agent up` succeeds and `azd ai agent show` reports the hosted
>   agent as healthy.
> - In DevUI, selecting the **marketing** agent answers campaign questions
>   from Cosmos+KB and live-web questions via `web_search`.

## Learning Resources

* [Hosted agents overview](https://learn.microsoft.com/azure/foundry/agents/concepts/hosted-agents)
* [Deploy a hosted agent (tutorial)](https://learn.microsoft.com/azure/foundry/agents/how-to/deploy-hosted-agent)
* [Foundry Toolbox & built-in tools](https://learn.microsoft.com/azure/ai-foundry/agents/tools)
* [Microsoft Agent Framework docs](https://learn.microsoft.com/agent-framework/)
* [Foundry IQ knowledge bases](https://learn.microsoft.com/azure/ai-foundry/foundry-iq)

## Tasks

| Task | Description |
| ---- | ----------- |
| [05.01 — Seed the Marketing Foundry IQ knowledge base](05_01_seed_marketing_kb.md) | Create the `zava-marketing-kb` KB and index marketing briefs. |
| [05.02 — Build the hosted Marketing agent](05_02_build_hosted_marketing_agent.md) | Implement `marketing_hosted/main.py` and `agent.yaml`. |
| [05.03 — Run locally, deploy to Foundry, talk to it in DevUI](05_03_deploy_and_wire.md) | `azd ai agent run` → `azd ai agent up` → DevUI. |

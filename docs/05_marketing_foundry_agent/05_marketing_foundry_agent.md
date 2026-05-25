---
title: 'Exercise 05: Marketing Prompt Agent (Foundry IQ + Code Interpreter)'
layout: default
nav_order: 7
has_children: true
---

# Exercise 05 — Build the Marketing Foundry Prompt Agent (Foundry IQ + Code Interpreter)

## Scenario

The Marketing team wants a specialist that can:

1. Reach authoritative Zava campaign data — the Marketing MCP server from
   Exercise 04 (Cosmos truth).
2. Ground answers on a corpus of campaign briefs and post-mortems — indexed
   into a **Foundry IQ knowledge base**.
3. Crunch numbers / make quick charts off whatever the MCP returns — via the
   Foundry **Code Interpreter** built-in tool.

We will register the agent as a regular **Foundry Prompt Agent** (same shape
as Products and Store-Ops in Exercises 03 and 06) and wire it into the chat
app, DevUI, and orchestrator. No hosted-agent runtime, no `azd ai agent`
extension, no extra Dockerfile.

> **Why not a Foundry-hosted Agent-Framework agent?** Hosted agents are great
> for production but introduce a separate Docker build, `azd ai agent up`,
> and `FOUNDRY_PROJECT_ENDPOINT` runtime. For a workshop we get the same
> behaviour by registering a Prompt Agent against the same MCP+KB tools.

## Description

You will:

1. Seed a **Foundry IQ knowledge base** (`zava-marketing-kb`) of marketing
   briefs alongside the existing Marketing MCP server.
2. Implement `src/foundry_agents/create_marketing_agent.py` — a small script
   that registers a Foundry Prompt Agent wired to three tools:
   - `MCPTool` → Marketing MCP server (Cosmos truth).
   - `CodeInterpreterTool` → Foundry-managed Python sandbox.
   - `MCPTool` → Marketing Foundry IQ KB (`knowledge_base_retrieve`).
3. Run the script to create/update the agent version on your Foundry project.
4. Talk to it from the **Agent Framework DevUI** and confirm the orchestrator
   routes campaign questions to it.

## Success Criteria

{: .success }
> - `zava-marketing-kb` Foundry IQ knowledge base exists and contains the
>   seeded marketing briefs.
> - `python -m src.foundry_agents.create_marketing_agent` succeeds and the
>   `zava-marketing-agent` agent version appears in the Foundry portal.
> - In DevUI, the **marketing** entity answers campaign questions using the
>   Marketing MCP and brief questions using the KB.

## Learning Resources

* [Foundry Prompt Agents](https://learn.microsoft.com/azure/ai-foundry/agents/concepts/prompt-agents)
* [Foundry Code Interpreter tool](https://learn.microsoft.com/azure/ai-foundry/agents/tools/code-interpreter)
* [Foundry IQ knowledge bases](https://learn.microsoft.com/azure/ai-foundry/foundry-iq)
* [Model Context Protocol (MCP)](https://modelcontextprotocol.io/)

## Tasks

| Task | Description |
| ---- | ----------- |
| [05.01 — Seed the Marketing Foundry IQ knowledge base](05_01_seed_marketing_kb.md) | Create the `zava-marketing-kb` KB and index marketing briefs. |
| [05.02 — Build the Marketing Prompt Agent](05_02_build_hosted_marketing_agent.md) | Implement `create_marketing_agent.py` wiring MCP + Code Interpreter + KB. |
| [05.03 — Register, run, wire into chat](05_03_deploy_and_wire.md) | Run the script and talk to the agent in DevUI. |

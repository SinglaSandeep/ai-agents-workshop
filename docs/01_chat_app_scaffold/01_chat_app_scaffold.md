---
title: 'Exercise 01: Scaffold the Chat App'
layout: default
nav_order: 3
has_children: true
---

# Exercise 01 — Scaffold the Zava Chat App

## Scenario

Before you build any AI, you want a working **frontend** you can point at every
new agent. Zava has asked for a single chat-style assistant that employees
can use to ask store-operations, product, and marketing questions.

This workshop ships **two complementary UIs** — you do not need to write
any HTML/JS:

1. **Agent Framework DevUI** — used in Exercises 01–06 to test each
   specialist agent on its own. Auto-generates a chat surface per agent
   and exposes an OpenAI-compatible Responses API.
2. **Zava Orchestrator Web UI** — a small FastAPI app introduced in
   Exercise 07. It shows the orchestrator's plan, the active agent, live
   execution trace, and the final answer — all updating in real time.

Every subsequent exercise creates a new Foundry agent that DevUI picks up
automatically, and the orchestrator UI lights up the corresponding box on
the workflow diagram when that agent is called.

## Description

In this exercise you will:

* Install the workshop package (already done in Exercise 00).
* Launch DevUI via `python -m src.app.devui_launch`.
* Open the DevUI chat surface in your browser.
* Read through `src/app/devui_launch.py` to understand how the three
  specialist Foundry agents are registered as DevUI entities.

## Success Criteria

{: .success }
> By the end of this exercise:
>
> - `python -m src.app.devui_launch` starts cleanly on port 8080.
> - <http://127.0.0.1:8080> shows the DevUI chat surface with three agents
>   listed (`products`, `marketing`, `store_ops`).
> - You understand that DevUI is used to test each agent **individually**
>   in Exercises 01–06, and that the **orchestrator web UI** (Exercise 07)
>   chats with all agents at once.
> - You can hit the Responses API at `POST /v1/responses` with `curl` or
>   the OpenAI Python SDK.

## Learning Resources

* [Agent Framework DevUI](https://github.com/microsoft/agent-framework/tree/main/python/packages/devui)
* [Foundry-Hosted Agent Framework demos (Azure-Samples)](https://github.com/Azure-Samples/foundry-hosted-agentframework-demos)
* [Microsoft Foundry — Agents overview](https://learn.microsoft.com/azure/ai-foundry/agents/overview)
* [Microsoft Agent Framework](https://learn.microsoft.com/azure/ai-foundry/agents/overview-agent-framework)

## Tasks

| Task | Description |
| ---- | ----------- |
| [01.01 — Run DevUI locally](01_01_run_app_locally.md) | Launch the Agent Framework DevUI and exchange messages with the stub agent. |
| [01.02 — Understand the DevUI launcher](01_02_understand_agent_mode.md) | Read `src/app/devui_launch.py` and learn how each later exercise registers a real agent. |

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
can use to ask HR, product, and marketing questions. In this workshop we use
the official **Microsoft Agent Framework DevUI** as that frontend — no
custom HTML/JS to maintain. DevUI auto-generates a chat surface for every
registered agent and exposes an OpenAI-compatible Responses API on the side.

Every subsequent exercise creates a new Foundry agent that DevUI then picks up
automatically — so you keep testing in the same browser tab as you go.

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
> - You understand that DevUI is the **only** UI in this workshop and that
>   every new Foundry agent shows up there with no extra wiring.
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

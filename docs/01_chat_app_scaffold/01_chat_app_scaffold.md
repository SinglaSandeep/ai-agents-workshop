---
title: 'Exercise 01: Scaffold the Chat App'
layout: default
nav_order: 3
has_children: true
---

# Exercise 01 — Scaffold the Pepsico Chat App

## Scenario

Before you build any AI, you want a working **frontend** you can point at every
new agent. Pepsico has asked for a single chat-style assistant that employees
can use to ask HR, product, and marketing questions. In this exercise you will
get the FastAPI + HTML chat application running locally and verify it routes
queries through a (temporary) stub backend.

Every subsequent exercise will replace this stub with a real agent — so you
keep testing in the browser as you go.

## Description

In this exercise you will:

* Install the workshop package (already done in Exercise 00).
* Launch the FastAPI server with `uvicorn`.
* Open the chat UI in your browser and exchange a few messages with the stub.
* Read through `src/app/main.py` to understand the `AGENT_MODE` switch that
  every later exercise will flip.

## Success Criteria

{: .success }
> By the end of this exercise:
>
> - `uvicorn src.app.main:app --reload --port 8000` starts cleanly.
> - <http://127.0.0.1:8000> shows the Pepsico chat UI.
> - Submitting any question returns the stub response: *"This application is
>   not yet ready to serve results…"*.
> - You can describe what `AGENT_MODE` will do in later exercises.

## Learning Resources

* [FastAPI in 5 minutes](https://fastapi.tiangolo.com/#example)
* [Microsoft Foundry — Agents overview](https://learn.microsoft.com/azure/ai-foundry/agents/overview)
* [Microsoft Agent Framework](https://learn.microsoft.com/azure/ai-foundry/agents/overview-agent-framework)

## Tasks

| Task | Description |
| ---- | ----------- |
| [01.01 — Run the chat app locally](01_01_run_app_locally.md) | Start uvicorn and exchange messages with the stub backend. |
| [01.02 — Understand `AGENT_MODE`](01_02_understand_agent_mode.md) | Read `main.py` and learn how each subsequent exercise wires in a real agent. |

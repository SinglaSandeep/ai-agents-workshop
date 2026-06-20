---
title: 'Exercise 01: Scaffold the Chat App'
layout: default
nav_order: 2
parent: 'Setup & Prerequisites'
has_children: false
---

# Exercise 01 — Scaffold the Zava Chat App

## Scenario

Before building any agents, you want a working **frontend**. Zava needs a
single chat assistant for store managers covering sales, inventory and
marketing.

This workshop ships **two complementary UIs** — you do not need to write
any HTML/JS:

1. **Zava Chat App** — a small FastAPI app (`src/app/main.py`) that is the
   real assistant you ship. It runs the full Intent → orchestrator → Response
   flow and streams the manager's plan, the active agent, and the final
   answer live. You start it now and keep it open as you build each agent.
2. **Agent Framework DevUI** — an optional debug surface that registers the
   whole Magentic workflow as a single entity (`zava_orchestrator`) so you
   can inspect the plan and intermediate agent calls. It becomes useful once
   the agents exist (Module 5).

Every subsequent exercise creates a new Foundry agent that the chat app calls
automatically — so the same browser tab starts answering more questions as you
go.

## What you will do

* Install the workshop package (already done in [Exercise 00](../00_setup/00_setup.md)).
* Launch the FastAPI chat app and open it in your browser.
* Understand how DevUI can later visualise the orchestrator.

## Steps

### 1. Launch the chat app

From the `ai-agents-workshop` folder, with your virtual environment active:

```powershell
uvicorn src.app.main:app --reload --port 8000
```

Open <http://127.0.0.1:8000>. The chat UI loads immediately.

{: .note }
> The agents don't exist in Foundry yet — that's what Exercises 02–09 across
> Modules 1–5 create. The page loads now, but a **business** question (e.g. about
> sales or inventory) won't return a full answer until you've built the agents
> and the orchestrator. To confirm the chat app itself works, send a simple
> greeting like *"Hello!"* first. As you finish each exercise, refresh the tab
> and try a business question again.

### 2. (Optional) Inspect the orchestrator in DevUI

Once you reach Module 5 you can launch the Agent Framework DevUI to watch the
Magentic plan and per-agent calls:

```powershell
python -m src.orchestrator.runner --devui
```

DevUI opens automatically (default port `8081`) and registers a single
`zava_orchestrator` entity — the whole workflow — not the individual agents.
Use the CLI runner to drive a one-off query instead:

```powershell
python -m src.orchestrator.runner --query "Which categories are trending this month?"
```

## Success criteria

{: .success }
> By the end of this exercise:
>
> - `uvicorn src.app.main:app --port 8000` starts cleanly.
> - <http://127.0.0.1:8000> shows the Zava chat UI in your browser.
> - You understand that the chat app is the shippable frontend and DevUI is an
>   optional debug view of the orchestrator (Module 5).

## Learning resources

* [Agent Framework DevUI](https://github.com/microsoft/agent-framework/tree/main/python/packages/devui)
* [Microsoft Foundry — Agents overview](https://learn.microsoft.com/azure/ai-foundry/agents/overview)
* [Microsoft Agent Framework](https://learn.microsoft.com/agent-framework/overview/agent-framework-overview)

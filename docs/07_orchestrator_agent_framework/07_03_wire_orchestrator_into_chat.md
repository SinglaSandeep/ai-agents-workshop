---
title: '3. Run the orchestrator in the web UI'
layout: default
nav_order: 3
parent: 'Exercise 07: Magentic Orchestrator'
---

# Task 07.03 — Run the Orchestrator in the Web UI

## Introduction

Up to now you tested each agent on its own in **DevUI**. In this task you
start the **Zava Orchestrator Web UI** — a small chat app that talks to
**all four agents at once** through the Magentic orchestrator you built in
Task 07.02.

The web UI shows you, in real time:

* the **workflow diagram** — boxes for each agent that light up as they are
  called, and turn green when they finish,
* the **execution trace** — a live timestamped log of every step
  (planner output, agent calls, errors),
* the **chat panel** — your question and the final grounded answer,
* the **plan** the orchestrator chose for your specific question.

You do not write any code in this task — just run the app and explore.

## Success Criteria

{: .success }
> By the end of this task:
>
> - `uvicorn src.app.main:app --reload --port 8000` starts cleanly.
> - <http://127.0.0.1:8000> shows the Zava UI with the workflow diagram on
>   the left and the chat panel on the right.
> - Asking a mixed-domain question lights up the relevant agent boxes,
>   adds rows to the **Execution Trace**, and produces a single final
>   answer in the chat.

## Key Tasks

### 01: Start the web UI

From the workshop root, with `.venv` activated and `.env` populated:

```powershell
uvicorn src.app.main:app --reload --port 8000
```

When you see `Uvicorn running on http://127.0.0.1:8000`, open that URL in
your browser.

{: .tip }
> Run this in its own terminal and leave it running for the rest of the
> workshop. The DevUI launcher from Exercise 01 uses a different port
> (8080), so you can keep both running side by side.

### 02: Tour the UI

The screen has three columns:

| Column | What it shows |
| ------ | ------------- |
| **Left — Agents & Knowledge Bases** | The names of the four specialist agents and the knowledge bases they read from. |
| **Center — Workflow + Execution Trace** | A diagram of the orchestrator flow. Boxes pulse **amber** while an agent is working and turn **green** when it finishes. Below the diagram, the **Execution Trace** records every step with a timestamp. |
| **Right — Chat** | The chat panel. Click any suggested question, or type your own and press **Send**. The status pill at the top right shows **Ready / Working / Error**. |

### 03: Ask a single-domain question

Click the **suggested question** *"List low-inventory paint SKUs at the
Seattle store"* (or type your own).

You should see:

* the **Orchestrator** box pulses amber, then the **Products Agent** box
  pulses,
* rows appear in the **Execution Trace** showing `INFO`, `ROUTE`, `QUERY`,
  `RESP`,
* the **Response** box turns green,
* the answer appears in the chat panel.

### 04: Ask a mixed-domain question

Now try a question that needs more than one agent, for example:

> *Spring Paint Sale at the Seattle store is soft. Which paint SKUs are low
> on inventory, what does last year's post-mortem suggest, and what
> discount can the Seattle store manager approve?*

You should see:

* the orchestrator plans the call sequence in the **Execution Trace**,
* the **Products**, **Marketing**, and **Store Ops** boxes each light up in
  turn,
* the **Response Generator** turns green last,
* the chat panel shows one polished final answer.

If the final answer looks like a raw transcript from one agent, the
**Response Generator** is not in your Foundry project yet — Exercise 08
creates it. The orchestrator will still work; the answer will just be less
polished.

### 05: Inspect what happened

* The **Execution Trace** panel is your "what just happened" log. Each row
  has a colored tag:
  * `INFO` — milestone (query received, workflow complete)
  * `ROUTE` — the manager's plan / progress update
  * `QUERY` — a specialist agent was called
  * `RESP` — a specialist agent returned an answer
  * `ERROR` — something went wrong (also shown in the chat as a red message)
* The **Clear** button at the top right of the trace empties the log
  without restarting the app.

### 06: Optional — run from the terminal instead

If you prefer the command line (or want machine-readable output for tests),
the same orchestrator is available as a CLI:

```powershell
python -m src.orchestrator.runner --query "What is our PTO policy?"
```

Add `--json` to also print the plan, per-agent transcripts, and raw events
as JSON at the end.

### 07: Optional — pick the orchestrator (manager) model per request

`stream_query` and `run_query` both accept an optional `manager_model`
kwarg that overrides the deployment passed to the Magentic *manager*.
This is what backs the **model dropdown** added to the chat UI when the
app is deployed to Container Apps (see [Exercise 13](../13_deploy_chat_app/13_deploy_chat_app.md)).

```python
# pick the model per-call without changing AZURE_AI_MODEL_DEPLOYMENT
result = await run_query(
    "What is our PTO policy?",
    manager_model="gpt-4o-mini",
)
```

In the FastAPI app the override is plumbed via the POST body:

```jsonc
// POST /chat/stream
{ "query": "What is our PTO policy?", "model": "gpt-4o-mini" }
```

`main.py` validates `model` against the `ORCHESTRATOR_MODEL_CHOICES` env
var allowlist before forwarding it to `stream_query`. Only the
**manager** swaps — hosted Foundry specialists keep the models defined
on their agent definitions.

## Troubleshooting

| Symptom | What to check |
| ------- | ------------- |
| `Error: HTTP 500` in the trace | Check the terminal running `uvicorn`. The most common cause is missing or wrong values in `.env`. |
| One specific agent box never lights up | That agent has not been created in Foundry yet, or its name in `.env` is wrong. Re-run the create script from the matching exercise. |
| The status pill stays on **Working** forever | Stop the request, check the terminal for a stack trace, then refresh the page. |
| `INFO Workflow complete. Plan: (none)` | The orchestrator returned without calling any specialist. Your question may be too off-topic — try one of the suggestions. |

## Next

Continue to [Exercise 08 — Response Generator](../08_response_generator/08_response_generator.md).

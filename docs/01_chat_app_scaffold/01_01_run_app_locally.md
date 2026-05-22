---
title: '1. Run the chat app locally'
layout: default
nav_order: 1
parent: 'Exercise 01: Scaffold the Chat App'
---

# Task 01.01 — Run the Chat App Locally

## Introduction

The workshop ships with a runnable FastAPI app at `src/app/main.py` and a
single-page HTML chat client at `src/app/chat.html`. The backend is wired to
return a hard-coded stub answer so you can exercise the UI before any real
agents exist.

## Success Criteria

* `uvicorn` starts the app on port 8000 with no errors.
* You can browse to <http://127.0.0.1:8000> and see the chat UI.
* Asking any question returns the stub response.

## Key Tasks

### 01: Start the server

In a terminal, from the repo root, activate your virtual environment and start
uvicorn.

<details markdown="block">
<summary><strong>Expand this section to view the solution</strong></summary>

```powershell
.\.venv\Scripts\Activate.ps1
uvicorn src.app.main:app --reload --port 8000
```

On macOS / Linux:

```bash
source .venv/bin/activate
uvicorn src.app.main:app --reload --port 8000
```

You should see uvicorn logs ending with:

```
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
```

</details>

### 02: Open the chat UI

Open <http://127.0.0.1:8000> in a browser. You should see the Pepsico chat
page. Submit the pre-filled question ("What is the PTO policy at Pepsico?").

You will get back something like:

> *This application is not yet ready to serve results. Please check back later.
> (You are seeing the Exercise 01 stub — set `AGENT_MODE` in `.env` after each
> exercise to wire in a real agent.)*

The `plan` row underneath shows a single `stub` pill. This confirms the
frontend, FastAPI server, and pydantic models are all wired up end-to-end.

### 03: Test the health endpoint

In a second terminal, hit the health endpoint:

```powershell
curl http://127.0.0.1:8000/health
```

You should get JSON similar to:

```json
{ "status": "ok", "agent_mode": "stub", "observability_enabled": false }
```

Leave the server running — every subsequent exercise re-uses the same chat
window for testing.

## Next

Continue to [01.02 — Understand `AGENT_MODE`](01_02_understand_agent_mode.md).

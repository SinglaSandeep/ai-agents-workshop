---
title: '2. Understand AGENT_MODE'
layout: default
nav_order: 2
parent: 'Exercise 01: Scaffold the Chat App'
---

# Task 01.02 — Understand `AGENT_MODE`

## Introduction

`src/app/main.py` reads an `AGENT_MODE` environment variable to decide which
backend handles `/chat`. As you complete each exercise, you will flip
`AGENT_MODE` to wire in the next agent without changing the frontend.

| `AGENT_MODE` | Wired in | Backend |
| ------------ | -------- | ------- |
| `stub` (default) | Exercise 01 | Hard-coded response |
| `products` | Exercise 03 | Products Foundry Prompt Agent (single agent) |
| `marketing` | Exercise 05 | Marketing Foundry Prompt Agent (single agent) |
| `hr` | Exercise 06 | HR Foundry Prompt Agent (Foundry IQ) |
| `orchestrator` | Exercise 07+ | Magentic multi-agent orchestrator |

## Success Criteria

* You can find and explain the `_dispatch()` function in `src/app/main.py`.
* You understand that changing `AGENT_MODE` in `.env` (and restarting uvicorn)
  is all that is required to switch backends.

## Key Tasks

### 01: Read `main.py`

Open [src/app/main.py](../../src/app/main.py) and read through:

* The `ChatRequest` / `ChatResponse` Pydantic models.
* The `/chat` route — note the `trace_span(...)` call (you will wire up
  observability in Exercise 08).
* The `_dispatch()` function — this is where each later exercise removes a
  `# TODO` comment and adds the call to the new agent runner.

### 02: Try changing the mode (optional)

Set `AGENT_MODE=products` in your `.env` file and restart uvicorn:

```powershell
$env:AGENT_MODE = "products"
uvicorn src.app.main:app --reload --port 8000
```

Submit a question. You will now get the *"not yet wired"* response with mode
set to `products`. That is exactly the gap Exercise 03 fills.

Set `AGENT_MODE=stub` again (or remove it) before moving on.

## Next

Continue to [Exercise 02 — Build & Deploy the Products MCP Server](../02_products_mcp_server/02_products_mcp_server.md).

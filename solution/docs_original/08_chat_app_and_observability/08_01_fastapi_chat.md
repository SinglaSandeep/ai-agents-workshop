---
title: '1. Run the FastAPI chat app'
layout: default
nav_order: 1
parent: 'Exercise 08: Chat App & Observability'
---

# Task 08.01 — Run the FastAPI Chat App

The app lives at [`src/app/main.py`](../../src/app/main.py). It exposes:

| Route | Purpose |
| ----- | ------- |
| `GET /` | Pepsico-branded chat HTML UI |
| `POST /chat` | `{ query }` → `{ final_answer, plan, transcripts, events }` |
| `GET /health` | Liveness + reports whether observability is wired |

## Steps

1. **Start the app**

   ```powershell
   uvicorn src.app.main:app --reload --port 8000
   ```

2. **Open the UI**

   Browse to <http://127.0.0.1:8000>. Try the questions you used to test the
   orchestrator. Watch the **Specialist transcripts** and **Orchestrator
   events** expanders to see what's happening under the hood.

3. **Run the CLI variant**

   ```powershell
   pepsico-workshop --query "Which Gatorade campaigns target youth athletes, and what's the PTO policy?"
   ```

   The CLI prints the plan and the final answer.

4. **Sanity check the API directly**

   ```powershell
   curl -s -X POST http://127.0.0.1:8000/chat `
     -H "Content-Type: application/json" `
     -d '{"query":"What is the PTO carryover policy?"}' | ConvertFrom-Json | Format-List
   ```

## Success criteria

{: .success }
> - `GET /health` returns `{"status":"ok","observability_enabled":<bool>}`
> - The browser UI returns a final answer plus a plan pill row
> - The CLI returns the same answer

## Next

[08.02 — Add observability to Application Insights / Foundry](08_02_observability.md).

---
title: '3. Wire the orchestrator into chat'
layout: default
nav_order: 3
parent: 'Exercise 07: Magentic Orchestrator'
---

# Task 07.03 — Run the Magentic Orchestrator From the Chat UI

## Introduction

The chat app already has an `orchestrator` branch in `_dispatch` that is
commented out. You uncomment it, flip `AGENT_MODE`, and ask mixed-domain
questions in the browser.

## Success Criteria

* With `AGENT_MODE=orchestrator`, the chat UI shows multiple pill names in
  the **Plan** row (e.g. `hr → products → response_generator`).

## Key Tasks

### 01: Activate the orchestrator branch in `main.py`

Open [src/app/main.py](../../src/app/main.py) and replace the
`return _not_yet_wired(...)` line in the `AGENT_MODE == "orchestrator"`
branch with the live call.

<details markdown="block">
<summary><strong>Expand this section to view the solution</strong></summary>

```python
    if AGENT_MODE == "orchestrator":
        from src.orchestrator.magentic_router import run_query

        result = await run_query(query)
        return {
            "final_answer": result.final_answer,
            "plan": result.plan,
            "transcripts": result.transcripts,
            "events": result.events,
            "mode": AGENT_MODE,
        }
```

</details>

### 02: Flip the mode and restart

```
AGENT_MODE=orchestrator
```

```powershell
uvicorn src.app.main:app --reload --port 8000
```

### 03: Try a mixed-domain prompt

In the browser, ask:

> *"Which active Gatorade campaigns target youth athletes, and what is the
> PTO policy for marketing managers attending those activations?"*

You should see the plan grow to several pills (`marketing → hr →
response_generator`) and the **Specialist transcripts** disclosure now
contains entries for each specialist.

If the **Final Answer** is just the HR transcript dumped raw, that means the
Response Generator agent does not exist yet — Exercise 08 fixes that.

## Next

Continue to [Exercise 08 — Response Generator](../08_response_generator/08_response_generator.md).

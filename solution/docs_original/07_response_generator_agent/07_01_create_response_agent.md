---
title: '1. Create the Response Generator agent'
layout: default
nav_order: 1
parent: 'Exercise 07: Response Generator'
---

# Task 07.01 — Create the Response Generator Foundry Agent

`src/foundry_agents/create_response_agent.py` is the simplest agent in the
workshop: no tools, only instructions.

## The key snippet

```python
create_or_update_agent(
    agent_name=settings.response_agent_name,
    instructions=INSTRUCTIONS,
    tools=[],
    description="Pepsico final-answer synthesiser.",
)
```

The instructions enforce:

- One direct sentence first.
- 1-3 supporting paragraphs (or bullets).
- `Sources:` line listing the specialists used, and any URLs from Bing.
- Pepsico-internal employee audience, warm but concise tone.

## Steps

1. **Run the script**

   ```powershell
   python -m src.foundry_agents.create_response_agent
   ```

2. **Verify in the Foundry portal**

   **Agents → pepsico-response-generator** → no tools, instructions visible.

## Success criteria

{: .success }
> - The Foundry portal shows the new agent with **zero** tools
> - The instructions match what's in the repo

## Next

[07.02 — Wire it into the orchestrator](07_02_wire_into_orchestrator.md).

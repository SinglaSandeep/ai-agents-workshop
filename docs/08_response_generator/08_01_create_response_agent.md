---
title: '1. Create the Response Generator agent'
layout: default
nav_order: 1
parent: 'Exercise 08: Response Generator'
---

# Task 08.01 — Create the Response Generator Agent

## Introduction

The Response Generator is a **tools-free** Prompt Agent. The orchestrator
hands it the user's original question plus the specialist transcripts; the
agent produces one polished reply in Pepsico voice.

## Success Criteria

* `python -m src.foundry_agents.create_response_agent` succeeds.
* `pepsico-response-generator` shows up in the Foundry portal with zero tools.

## Key Tasks

### 01: Implement `main()`

Open [src/foundry_agents/create_response_agent.py](https://github.com/SinglaSandeep/ai-agents-workshop/blob/main/src/foundry_agents/create_response_agent.py).

<details markdown="block">
<summary><strong>Expand this section to view the solution</strong></summary>

```python
"""Create the Response Generator Foundry Prompt Agent (no tools)."""

from __future__ import annotations

import logging

from src.common.settings import get_settings

from ._common import create_or_update_agent

INSTRUCTIONS = """You are the Pepsico Response Generator.

You receive a JSON object with the user's original question and the answers
produced by one or more specialists ("hr", "products", "marketing"). Produce
the final reply for the user.

Rules:
- Lead with a single direct sentence answering the question.
- Then 1-3 short paragraphs of supporting detail. Use bullet points if helpful.
- Merge information from multiple specialists when relevant; never invent facts.
- If specialists conflict, prefer Pepsico's internal sources over web search.
- End with a `Sources:` line listing the specialists used and any URLs.
- Tone: warm, professional, concise. Pepsico-internal employees are the audience.
"""


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    settings = get_settings()
    create_or_update_agent(
        agent_name=settings.response_agent_name,
        instructions=INSTRUCTIONS,
        tools=[],
        description="Pepsico final-answer synthesiser.",
    )


if __name__ == "__main__":
    main()
```

</details>

### 02: Run it

```powershell
python -m src.foundry_agents.create_response_agent
```

## Next

Continue to [08.02 — Verify the orchestrator hand-off](08_02_wire_into_orchestrator.md).

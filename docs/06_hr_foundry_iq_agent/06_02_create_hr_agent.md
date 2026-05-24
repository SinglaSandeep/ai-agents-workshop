---
title: '2. Create the HR Prompt Agent'
layout: default
nav_order: 2
parent: 'Exercise 06: HR Foundry IQ Agent'
---

# Task 06.02 — Create the HR Foundry Prompt Agent

## Introduction

The HR agent has a single MCP tool — the `knowledge_base_retrieve` operation
exposed by the Foundry IQ knowledge base you created in the previous task.
By limiting `allowed_tools` you make sure the model cannot call any other
admin operations on the Search service.

## Success Criteria

* `python -m src.foundry_agents.create_hr_agent` succeeds.
* The new agent has one MCP tool, with `allowed_tools=["knowledge_base_retrieve"]`.

## Key Tasks

### 01: Implement `main()`

Open [src/foundry_agents/create_hr_agent.py](https://github.com/SinglaSandeep/ai-agents-workshop/blob/main/src/foundry_agents/create_hr_agent.py).

<details markdown="block">
<summary><strong>Expand this section to view the solution</strong></summary>

```python
"""Create the HR Foundry Prompt Agent grounded by a Foundry IQ KB."""

from __future__ import annotations

import logging

from azure.ai.projects.models import MCPTool

from src.common.settings import get_settings

from ._common import create_or_update_agent

LOG = logging.getLogger(__name__)

INSTRUCTIONS = """You are the Pepsico HR Assistant.

Your only source of truth is the connected Foundry IQ knowledge base of Pepsico HR
policies. For every answer you MUST:

1. Call the `knowledge_base_retrieve` tool with a focused question.
2. Answer only from the retrieved content. If the answer is not there, say:
   "I could not find this in the current Pepsico HR knowledge base. Please contact
   your HR business partner."
3. End every answer with a `Sources:` line listing the cited document filenames.
"""


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    settings = get_settings()

    if not settings.azure_search_endpoint:
        raise RuntimeError("AZURE_SEARCH_ENDPOINT must be set.")

    mcp_endpoint = (
        f"{settings.azure_search_endpoint.rstrip('/')}"
        f"/knowledgebases/{settings.hr_kb_name}/mcp?api-version=2025-11-01-preview"
    )

    hr_kb_tool = MCPTool(
        server_label="hr-knowledge-base",
        server_url=mcp_endpoint,
        require_approval="never",
        allowed_tools=["knowledge_base_retrieve"],
        project_connection_id=settings.hr_kb_connection_name,
    )

    create_or_update_agent(
        agent_name=settings.hr_agent_name,
        instructions=INSTRUCTIONS,
        tools=[hr_kb_tool],
        description="Pepsico HR specialist grounded by Foundry IQ.",
    )


if __name__ == "__main__":
    main()
```

</details>

### 02: Run it

```powershell
python -m src.foundry_agents.create_hr_agent
```

## Next

Continue to [06.03 — Wire the agent into the chat UI](06_03_wire_into_chat_app.md).

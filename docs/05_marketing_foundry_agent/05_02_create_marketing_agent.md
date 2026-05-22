---
title: '2. Create the Marketing Prompt Agent'
layout: default
nav_order: 2
parent: 'Exercise 05: Marketing Foundry Agent (+ Bing)'
---

# Task 05.02 — Create the Marketing Foundry Prompt Agent

## Introduction

You will fill in `create_marketing_agent.py` so the script registers the
Marketing MCP connection and creates an agent with **two** tools attached:

* `MCPTool` → Marketing MCP server
* `WebSearchTool` → Bing Grounding

The `INSTRUCTIONS` block in the starter file already tells the agent when to
prefer MCP vs Bing.

## Success Criteria

* `python -m src.foundry_agents.create_marketing_agent` succeeds.
* The new agent version shows two tools in the Foundry portal.

## Key Tasks

### 01: Implement `main()`

Open [src/foundry_agents/create_marketing_agent.py](../../src/foundry_agents/create_marketing_agent.py).

<details markdown="block">
<summary><strong>Expand this section to view the solution</strong></summary>

```python
"""Create the Pepsico Marketing Foundry Prompt Agent."""

from __future__ import annotations

import logging

from azure.ai.projects.models import MCPTool, WebSearchTool

from src.common.foundry_client import upsert_project_connection
from src.common.settings import get_settings

from ._common import create_or_update_agent

LOG = logging.getLogger(__name__)

INSTRUCTIONS = """You are the Pepsico Marketing Specialist.

You have two tools:

1. The `pepsico-marketing` MCP server, which is the source of truth for ALL
   Pepsico campaign data (status, budget, channels, KPIs, etc.). Use it first
   for any question about Pepsico campaigns.

2. The web search tool (Grounding with Bing). Use it ONLY for:
   - Live news about Pepsico brands or competitors.
   - Public market context (industry trends, competitor announcements).
   - Any question that requires information after the model's training cutoff.

Rules:
- Never make up Pepsico campaign data. If the MCP tool returns nothing, say so.
- When you cite the web, include the URL.
- Always finish with a one-line summary of which tool you used and why.
"""


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    settings = get_settings()

    if not settings.marketing_mcp_url:
        raise RuntimeError(
            "MARKETING_MCP_URL is empty. Deploy the Marketing MCP server (Exercise 04) first."
        )

    upsert_project_connection(
        connection_name=settings.marketing_mcp_connection_name,
        category="RemoteTool",
        target=settings.marketing_mcp_url,
        auth_type="ProjectManagedIdentity",
        audience="https://management.azure.com/",
        metadata={"ApiType": "MCP"},
    )

    marketing_tool = MCPTool(
        server_label="pepsico-marketing",
        server_url=settings.marketing_mcp_url,
        require_approval="never",
        project_connection_id=settings.marketing_mcp_connection_name,
    )
    web_search_tool = WebSearchTool()

    create_or_update_agent(
        agent_name=settings.marketing_agent_name,
        instructions=INSTRUCTIONS,
        tools=[marketing_tool, web_search_tool],
        description="Pepsico Marketing specialist (Cosmos-backed MCP + Bing Grounding).",
    )


if __name__ == "__main__":
    main()
```

</details>

### 02: Run it

```powershell
python -m src.foundry_agents.create_marketing_agent
```

### 03: Verify in the portal

Foundry portal → **Agents → pepsico-marketing-agent → Latest version**.
Confirm two tools: **MCP** and **Grounding with Bing Search**.

## Next

Continue to [05.03 — Wire the agent into the chat UI](05_03_wire_into_chat_app.md).

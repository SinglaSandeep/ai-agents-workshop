---
title: '2. Create the Products Prompt Agent'
layout: default
nav_order: 2
parent: 'Exercise 03: Products Foundry Agent'
---

# Task 03.02 — Create the Products Foundry Prompt Agent

## Introduction

A **Foundry Prompt Agent** is a server-side, versioned bundle of:

* a model deployment name (e.g. `gpt-4.1-mini`),
* an `instructions` system prompt,
* a list of `tools`.

You will write a small script that creates (or updates) a new agent version
named `zava-products-agent`, attaching the MCP connection from the previous
task.

## Success Criteria

* `python -m src.foundry_agents.create_products_agent` runs cleanly.
* The log line `Created agent 'zava-products-agent' version '<id>'` appears.
* The agent shows up in the Foundry portal under **Agents** with a single
  `MCPTool`.

## Key Tasks

### 01: Open the starter script

Open [src/foundry_agents/create_products_agent.py](https://github.com/SinglaSandeep/ai-agents-workshop/blob/main/src/foundry_agents/create_products_agent.py).
The `INSTRUCTIONS` block is already filled in. You just need to implement
`main()` — read its TODO comments.

### 02: Implement `main()`

<details markdown="block">
<summary><strong>Expand this section to view the solution</strong></summary>

```python
"""Create the Zava Products Foundry Prompt Agent."""

from __future__ import annotations

import logging

from azure.ai.projects.models import MCPTool

from src.common.foundry_client import upsert_project_connection
from src.common.settings import get_settings

from ._common import create_or_update_agent

LOG = logging.getLogger(__name__)

INSTRUCTIONS = """You are the Zava Products Specialist.

You have access to the `Zava-products` MCP server which exposes:
  - list_categories()
  - list_products(category, limit)
  - get_product(product_id)
  - search_products(text, limit)

Rules:
1. Pick the most specific tool for the user's question.
2. Only answer using data returned by the tools — never invent products,
   SKUs, prices, or sizes.
3. When you cite a product, include its `id` (e.g. `ZV-PNT-001`) and `name`.
4. If the catalog has no match, say so plainly and suggest a related category.
"""


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    settings = get_settings()

    if not settings.products_mcp_url:
        raise RuntimeError(
            "PRODUCTS_MCP_URL is empty. Deploy the Products MCP server in Exercise 02 first."
        )

    # 1. Project connection that owns the URL + auth.
    upsert_project_connection(
        connection_name=settings.products_mcp_connection_name,
        category="RemoteTool",
        target=settings.products_mcp_url,
        auth_type="ProjectManagedIdentity",
        audience="https://management.azure.com/",
        metadata={"ApiType": "MCP"},
    )

    # 2. The agent's view of that connection.
    products_tool = MCPTool(
        server_label="Zava-products",
        server_url=settings.products_mcp_url,
        require_approval="never",
        project_connection_id=settings.products_mcp_connection_name,
    )

    create_or_update_agent(
        agent_name=settings.products_agent_name,
        instructions=INSTRUCTIONS,
        tools=[products_tool],
        description="Zava Products specialist (MCP-backed by Cosmos DB).",
    )


if __name__ == "__main__":
    main()
```

</details>

### 03: Run it

```powershell
python -m src.foundry_agents.create_products_agent
```

Expected log lines:

```
INFO Upserting Foundry project connection zava-products-mcp-conn
INFO Creating agent version: zava-products-agent (model=gpt-4.1-mini, tools=1)
INFO Created agent 'zava-products-agent' version '1'
```

### 04: Verify in the portal

Open the Foundry portal → your project → **Agents → zava-products-agent**.
Confirm:

* Latest version has one tool of type **MCP**.
* Connection name in the tool matches `PRODUCTS_MCP_CONNECTION_NAME`.

## Next

Continue to [03.03 — Wire the agent into the chat UI](03_03_wire_into_chat_app.md).

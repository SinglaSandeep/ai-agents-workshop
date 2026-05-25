---
title: '2. Build the Marketing Prompt Agent'
layout: default
nav_order: 2
parent: 'Exercise 05: Marketing Prompt Agent (Foundry IQ + Code Interpreter)'
---

# Task 05.02 — Build the Marketing Prompt Agent

## Introduction

A **Foundry Prompt Agent** is a versioned, server-side agent that lives on
your Foundry project. You describe it once (model, instructions, tools) by
calling `project.agents.create_version(...)`; from then on anything that
resolves the agent by name — chat app, DevUI, orchestrator, evaluations —
can talk to it without any extra runtime.

The Marketing agent gets three tools:

1. **Marketing MCP** (`MCPTool`) — the Cosmos-backed campaign server from
   Exercise 04 (`list_campaigns`, `get_campaign`, `search_campaigns`,
   `list_campaigns_by_store`, `list_campaigns_by_category`).
2. **Code Interpreter** (`CodeInterpreterTool`) — Foundry-managed Python
   sandbox for totals, comparisons, and quick charts on data the MCP returns.
3. **Marketing IQ KB** (`MCPTool`) — the `zava-marketing-kb` knowledge base
   from Task 05.01, reached over its `knowledge_base_retrieve` MCP endpoint.

The script lives at [src/foundry_agents/create_marketing_agent.py](https://github.com/SinglaSandeep/ai-agents-workshop/blob/main/src/foundry_agents/create_marketing_agent.py)
and follows the same `create_or_update_agent` pattern as Products
(Exercise 03) and Store-Ops (Exercise 06).

## Success Criteria

* `src/foundry_agents/create_marketing_agent.py` wires all three tools above
  and calls `create_or_update_agent(...)` with
  `agent_name=settings.marketing_agent_name`.
* The script asserts that `MARKETING_MCP_URL` and
  `AZURE_SEARCH_ENDPOINT` are set, and registers the two project
  connections used by the MCP tools.

## Key Tasks

### 01: Review the script

Open the file. The interesting bits:

```python
from azure.ai.projects.models import CodeInterpreterTool, MCPTool

from src.common.foundry_client import upsert_project_connection
from src.common.settings import get_settings
from ._common import create_or_update_agent

# 1) Marketing MCP server (Cosmos truth).
upsert_project_connection(
    connection_name=settings.marketing_mcp_connection_name,
    category="RemoteTool",
    target=settings.marketing_mcp_url,
    auth_type="None",
    metadata={"ApiType": "MCP"},
)
tools.append(
    MCPTool(
        server_label="zava-marketing",
        server_url=settings.marketing_mcp_url,
        require_approval="never",
        project_connection_id=settings.marketing_mcp_connection_name,
    )
)

# 2) Code Interpreter (no connection required).
tools.append(CodeInterpreterTool())

# 3) Foundry IQ KB MCP (Marketing briefs + post-mortems).
kb_url = (
    f"{settings.azure_search_endpoint.rstrip('/')}"
    f"/knowledgebases/{settings.marketing_kb_name}"
    "/mcp?api-version=2025-11-01-preview"
)
tools.append(
    MCPTool(
        server_label="marketing-knowledge-base",
        server_url=kb_url,
        require_approval="never",
        allowed_tools=["knowledge_base_retrieve"],
        project_connection_id=settings.marketing_kb_connection_name,
    )
)

create_or_update_agent(
    agent_name=settings.marketing_agent_name,
    instructions=INSTRUCTIONS,
    tools=tools,
    model=settings.azure_ai_model_deployment,
    description="...",
)
```

> **Why `upsert_project_connection` for the MCP tools?** Foundry binds an
> `MCPTool` to a **project connection** that pins the URL and (optionally)
> auth. `upsert_project_connection` is idempotent — safe to re-run.

### 02: Review the instructions

The instructions explicitly tell the model:

* When to prefer the MCP vs the KB (structured vs narrative).
* To always cite `campaign_id` / `store_id` / `category_id` / `product_id`.
* That it has **no** web-search tool, so it should not pretend to fetch
  live news.
* To end every answer with `Tools used: ...`.

### 03: (Optional) Add a Bing Grounding tool later

If you later set up a *Grounding with Bing Search* connection on the
project, you can add it with `BingGroundingTool` next to the MCP tools and
update the instructions to allow live web answers. The workshop intentionally
ships without it.

## Next

Continue to [05.03 — Register, run, wire into chat](05_03_deploy_and_wire.md).

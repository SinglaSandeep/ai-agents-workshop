---
title: '2. Build the FastMCP server'
layout: default
nav_order: 2
parent: 'Exercise 04: Marketing MCP Server'
---

# Task 04.02 — Build the Marketing MCP Server

## Introduction

The Marketing server mirrors the Products one but exposes **five** tools
because marketing teams care about KPIs:

| Tool | Purpose |
| ---- | ------- |
| `list_active_campaigns(limit)` | What is running today |
| `list_campaigns_by_brand(brand, limit)` | Drill into one brand |
| `get_campaign(id)` | Full record for a campaign |
| `search_campaigns(text, limit)` | Free-text questions |
| `campaign_performance(id)` | KPIs only — for ROI questions |

## Success Criteria

* `src/mcp_servers/marketing/cosmos_repo.py` implements all five methods.
* `src/mcp_servers/marketing/server.py` exposes five `@mcp.tool` functions
  on a streamable-HTTP ASGI app at `/mcp`.

## Key Tasks

### 01: Implement `cosmos_repo.py`

Open [src/mcp_servers/marketing/cosmos_repo.py](https://github.com/SinglaSandeep/ai-agents-workshop/blob/main/src/mcp_servers/marketing/cosmos_repo.py)
and follow the TODOs. As with the Products repo, every method must emit
one structured log line via the `_log_query` helper on the
`zava.mcp.marketing.cosmos` logger so each Cosmos query the agent
triggers is auditable.


### 02: Implement `server.py`

Open [src/mcp_servers/marketing/server.py](https://github.com/SinglaSandeep/ai-agents-workshop/blob/main/src/mcp_servers/marketing/server.py).


### 03: Smoke-test locally

```powershell
zava-marketing-mcp
# in another terminal
npx @modelcontextprotocol/inspector
```

Connect the Inspector to `http://127.0.0.1:8002/mcp` and confirm all five
tools are listed.

## Next

Continue to [04.03 — Deploy to Azure Container Apps](04_03_deploy_container_app.md).

---
title: '2. Walk through the server code'
layout: default
nav_order: 2
parent: 'Exercise 02: Marketing MCP Server'
---

# Task 02.02 — Understand the Marketing MCP Server

The layout mirrors Exercise 01:

```
src/mcp_servers/marketing/
├── __init__.py
├── server.py            # FastMCP app + 5 tools
├── cosmos_repo.py       # Cosmos queries
├── Dockerfile
├── requirements.txt
└── seed/
    ├── marketing_seed.json
    └── seed_cosmos.py
```

## Differences from the Products server

| Aspect | Products | Marketing |
| ------ | -------- | --------- |
| Container | `products` | `marketing_campaigns` |
| Default port | `8001` | `8002` |
| `mcp.name` | `pepsico-products` | `pepsico-marketing` |
| Tools | 4 (catalog ops) | 5 (incl. **`campaign_performance`** which composes a smaller projection) |
| Sample size | 12 SKUs | 8 campaigns |

## Why `campaign_performance` is a separate tool

We could return KPIs as part of `get_campaign`. We don't because:

1. The agent often needs **only** the KPIs and the Foundry token budget
   benefits from a smaller payload.
2. Surfacing a dedicated `campaign_performance` tool gives the LLM a stronger
   semantic signal — it picks the right tool for ROI/CTR questions.

This is a common pattern: prefer **many small tools with clear names** over
one large tool with a JSON shape the model has to interpret.

## Success criteria

{: .success }
> - You can list each of the 5 tools and explain when the agent should pick each
> - You understand why `campaign_performance` is separate from `get_campaign`

## Next

[02.03 — Run locally and deploy to ACA](02_03_deploy_container_app.md).

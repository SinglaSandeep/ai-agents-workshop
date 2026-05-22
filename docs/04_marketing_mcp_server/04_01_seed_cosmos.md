---
title: '1. Seed Cosmos DB with marketing data'
layout: default
nav_order: 1
parent: 'Exercise 04: Marketing MCP Server'
---

# Task 04.01 — Seed Cosmos DB With Marketing Campaign Data

## Introduction

The Marketing MCP server is read-only; before you can run it you need to load
the seed campaigns into Cosmos. We ship a JSON file and a one-shot seed
script that mirrors the Products seed from Exercise 02.

## Success Criteria

* The `marketing_campaigns` container exists in the `pepsico` database.
* All campaigns from `marketing_seed.json` are upserted.

## Key Tasks

### 01: Inspect the seed file

Open [src/mcp_servers/marketing/seed/marketing_seed.json](../../src/mcp_servers/marketing/seed/marketing_seed.json).
Each document looks like:

```json
{
  "id": "CMP-2026-001",
  "campaign_name": "Gatorade Hydrate Summer",
  "brand": "Gatorade",
  "status": "active",
  "region": "North America",
  "channel": ["TV", "Social", "OOH"],
  "target_audience": "Youth athletes (13-22)",
  "budget_usd": 3500000,
  "impressions": 12500000,
  "clicks": 215000,
  "ctr": 0.0172,
  "conversions": 18200,
  "spend_usd": 2950000,
  "roi": 2.4,
  "summary": "..."
}
```

### 02: Run the seed

```powershell
pepsico-seed-marketing
```

Expected log:

```
INFO Using database 'pepsico'
INFO Created container 'marketing_campaigns'
INFO Upserted N campaigns
```

### 03: Verify

Open Cosmos **Data Explorer → pepsico → marketing_campaigns → Items**.
Confirm the documents appear.

## Next

Continue to [04.02 — Build the FastMCP server](04_02_build_mcp_server.md).

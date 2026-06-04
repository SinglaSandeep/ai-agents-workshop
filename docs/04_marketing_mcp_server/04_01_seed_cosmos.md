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

* The `marketing_campaigns` container exists in the `zava` database.
* All campaigns from `marketing_seed.json` are upserted.

## Key Tasks

### 01: Inspect the seed file

Open [src/mcp_servers/marketing/seed/marketing_seed.json](https://github.com/SinglaSandeep/ai-agents-workshop/blob/main/src/mcp_servers/marketing/seed/marketing_seed.json).
Each document looks like:

```json
{
  "id": "CMP-2026-001",
  "campaign_name": "Spring Paint Sale 2026",
  "brand": "Zava",
  "status": "active",
  "region": "North America",
  "channel": ["TV", "Social", "OOH"],
  "target_audience": "DIY homeowners (25-54)",
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

### 02: Create the container (control plane)

The `zava` database already exists from Exercise 02. Create the
`marketing_campaigns` container via the Azure control plane (the Cosmos data
plane role cannot create containers):

```powershell
$account = "<your-cosmos-account-name>"
$rg      = "<your-resource-group>"

az cosmosdb sql container create `
  --account-name $account --resource-group $rg `
  --database-name Zava --name marketing_campaigns --partition-key-path /id
```

### 03: Run the seed

From the workshop root with the venv activated:

```powershell
python -m src.mcp_servers.marketing.seed.seed_cosmos
```

Expected log:

```
INFO Seeding database 'zava' container 'marketing_campaigns'
INFO Upserted 50 campaigns
```

### 04: Verify

Open Cosmos **Data Explorer → Zava → marketing_campaigns → Items**.
Confirm 50 documents (`CMP-2026-001` …) appear.

## Next

Continue to [04.02 — Build the FastMCP server](04_02_build_mcp_server.md).

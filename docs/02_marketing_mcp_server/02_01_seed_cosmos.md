---
title: '1. Seed Cosmos DB with campaign data'
layout: default
nav_order: 1
parent: 'Exercise 02: Marketing MCP Server'
---

# Task 02.01 — Seed Cosmos DB with Marketing Campaigns

## Steps

1. **Run the seed script**

   ```powershell
   pepsico-seed-marketing
   ```

   Expected tail:

   ```text
   INFO Using database 'pepsico'
   INFO Created container 'marketing_campaigns'
   INFO Upserted 8 campaigns
   ```

2. **Inspect in Data Explorer**

   Portal → Cosmos DB → **Data Explorer → pepsico → marketing_campaigns → Items**
   should show 8 documents with ids `CMP-2026-001` through `CMP-2026-008`.

3. **(Optional) Run a sanity query**

   ```powershell
   python -c "from src.mcp_servers.marketing.cosmos_repo import MarketingRepository; import json; r=MarketingRepository(); print(json.dumps(r.list_active_campaigns(limit=3), indent=2, default=str))"
   ```

## Success criteria

{: .success }
> - The seed script reports `Upserted 8 campaigns`
> - Data Explorer shows all 8 documents
> - The list-active probe returns at least 3 campaigns

## Next

[02.02 — Walk through the MCP server code](02_02_build_mcp_server.md).

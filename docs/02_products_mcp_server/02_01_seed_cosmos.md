---
title: '1. Seed Cosmos DB with product data'
layout: default
nav_order: 1
parent: 'Exercise 02: Products MCP Server'
---

# Task 02.01 — Seed Cosmos DB With Product Data

## Introduction

The MCP server you build in the next task is a thin wrapper over a Cosmos DB
container. Before you can run it, you need data. We ship a JSON file with
65 representative Zava SKUs and a one-shot seed script.

## Success Criteria

* A `zava` database exists on your Cosmos DB account.
* A `products` container with `/id` partition key exists inside it.
* 65 documents are upserted into the container.

## Key Tasks

### 01: Inspect the seed data

Open [src/mcp_servers/products/seed/products_seed.json](https://github.com/SinglaSandeep/ai-agents-workshop/blob/main/src/mcp_servers/products/seed/products_seed.json)
and look at the document shape:

```json
{
  "id": "ZV-PNT-001",
  "name": "Pepsi Cola",
  "brand": "Pepsi",
  "category": "Beverages",
  "size": "12 oz can (12-pack)",
  "description": "Classic Pepsi cola in a 12-pack of 12 oz cans.",
  "calories": 150,
  "price_usd": 6.99
}
```

Each document uses `id` as both the document id and the partition key.

### 02: Create the database and container (control plane)

The `Cosmos DB Built-in Data Contributor` data-plane role grants item-level
read/write but **not** `sqlDatabases/write` or `containers/write`. Create
the database and container once via the Azure control plane (your Azure user
needs `Contributor` on the Cosmos account or resource group):

```powershell
$account = "<your-cosmos-account-name>"
$rg      = "<your-resource-group>"

az cosmosdb sql database create `
  --account-name $account --resource-group $rg --name zava

az cosmosdb sql container create `
  --account-name $account --resource-group $rg `
  --database-name Zava --name products --partition-key-path /id
```

If either resource already exists the command is a no-op.

### 03: Run the seed script

From an activated venv at the repo root, run:

```powershell
python -m src.mcp_servers.products.seed.seed_cosmos
```

This runs `src/mcp_servers/products/seed/seed_cosmos.py` which upserts every
document from the seed JSON into the existing container. You should see:

```
INFO Seeding database 'zava' container 'products'
INFO Upserted 65 products
```


### 04: Verify in the portal

Open the Cosmos DB account in the Azure portal → **Data Explorer**. You
should see `zava → products → Items` with 48 documents (`ZV-PNT-001` …).

## Next

Continue to [02.02 — Build the FastMCP server](02_02_build_mcp_server.md).

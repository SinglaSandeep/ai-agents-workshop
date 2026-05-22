---
title: '1. Seed Cosmos DB with product data'
layout: default
nav_order: 1
parent: 'Exercise 02: Products MCP Server'
---

# Task 02.01 — Seed Cosmos DB With Product Data

## Introduction

The MCP server you build in the next task is a thin wrapper over a Cosmos DB
container. Before you can run it, you need data. We have shipped a JSON file
with 12 representative Pepsico SKUs and a one-shot seed script.

## Success Criteria

* A `pepsico` database exists on your Cosmos DB account.
* A `products` container with `/id` partition key exists inside it.
* 12 documents are upserted into the container.

## Key Tasks

### 01: Inspect the seed data

Open [src/mcp_servers/products/seed/products_seed.json](../../src/mcp_servers/products/seed/products_seed.json)
and look at the document shape:

```json
{
  "id": "PEP-001",
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

### 02: Run the seed script

From an activated venv, run:

```powershell
pepsico-seed-products
```

This calls `src/mcp_servers/products/seed/seed_cosmos.py` which:

1. Creates the `pepsico` database if it does not exist.
2. Creates the `products` container if it does not exist (`/id` partition key).
3. Upserts every document from the seed JSON.

You should see:

```
INFO Using database 'pepsico'
INFO Created container 'products'
INFO Upserted 12 products
```

<details markdown="block">
<summary><strong>Expand this section if the seed script errors</strong></summary>

The most common errors are:

* **`COSMOS_ENDPOINT is not set`** — finish Exercise 00 first.
* **`403 Forbidden`** — your user is missing the
  `Cosmos DB Built-in Data Contributor` role. See the troubleshooting block
  in [Task 00.04](../00_setup/00_04_verify_environment.md).
* **`HttpResponseError: ServiceUnavailable`** — Cosmos throttling; rerun the
  script after 30 seconds.

</details>

### 03: Verify in the portal

Open the Cosmos DB account in the Azure portal → **Data Explorer**. You
should see `pepsico → products → Items` with 12 documents (`PEP-001` … `PEP-012`).

## Next

Continue to [02.02 — Build the FastMCP server](02_02_build_mcp_server.md).

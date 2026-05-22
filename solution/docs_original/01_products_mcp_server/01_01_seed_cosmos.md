---
title: '1. Seed Cosmos DB with product data'
layout: default
nav_order: 1
parent: 'Exercise 01: Products MCP Server'
---

# Task 01.01 — Seed Cosmos DB

The seed script `src/mcp_servers/products/seed/seed_cosmos.py` creates the
`pepsico` database and the `products` container (partitioned by `/id`) if
they do not exist, then upserts 12 sample SKUs from
`products_seed.json`.

## Steps

1. **Confirm `COSMOS_ENDPOINT` and `COSMOS_DATABASE` are set in `.env`** (you
   did this in [00.03](../00_setup/00_03_verify_resources.md)).

2. **Run the seed script**

   ```powershell
   pepsico-seed-products
   ```

   Expected tail of the output:

   ```text
   INFO Using database 'pepsico'
   INFO Created container 'products'           # or "already exists" on a re-run
   INFO Upserted 12 products
   ```

3. **Verify in the portal**

   Portal → Cosmos DB account → **Data Explorer → pepsico → products → Items**
   should show 12 documents with ids `PEP-001` through `PEP-012`.

4. **(Optional) Run a sanity query**

   ```powershell
   python -c "from src.mcp_servers.products.cosmos_repo import ProductsRepository; import json; print(json.dumps(ProductsRepository().search_products('Gatorade'), indent=2))"
   ```

   You should see at least the Gatorade Lemon-Lime SKU returned.

## Success criteria

{: .success }
> - The seed script reports `Upserted 12 products`
> - Portal shows the 12 documents in the `products` container
> - The Python sanity query returns at least 1 match

## Next

[01.02 — Walk through the MCP server code](01_02_build_mcp_server.md).

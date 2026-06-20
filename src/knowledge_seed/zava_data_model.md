# Zava DIY Retail — Shared Data Model

Zava is a Pacific Northwest DIY hardware retailer. Every specialist agent in
the workshop reasons over the **same business entities**, joined on three
shared keys that show up in every Cosmos document, every Markdown KB doc, and
every agent prompt:

| Key           | Values                                                                              |
|---------------|-------------------------------------------------------------------------------------|
| `store_id`    | `seattle`, `bellevue`, `tacoma`, `redmond`, `kirkland`, `spokane`, `everett`, `online` |
| `category_id` | `paint`, `power-tools`, `hand-tools`, `garden`, `lumber`, `electrical`, `plumbing`, `hardware` |
| `product_id`  | `ZV-<CAT>-NNN` (e.g. `ZV-PNT-001` for a paint SKU, `ZV-PWT-014` for a power tool)   |

This is why the Magentic orchestrator has work to do — answering a single
question like *"Sales for our Spring Paint Sale in Seattle look soft — which
SKUs are low on inventory, what does last year's post-mortem suggest, and
what's the discount-approval policy for the Seattle store manager?"* requires
joining facts across all three agents on `store_id="seattle"` and
`category_id="paint"`.

## Agent → backend → key mapping

| Agent                  | Backend(s)                                            | Reasons over                |
|------------------------|--------------------------------------------------------|-----------------------------|
| `zava-products-agent`  | Cosmos MCP (`products` container)                      | `product_id`, `category_id`, `store_id` (inventory_by_store) |
| `zava-marketing-agent` | Cosmos MCP (`campaigns`) + Foundry IQ AI Search (briefs / post-mortems) + Foundry Toolbox web_search | `category_id`, `store_id`, `product_id` |
| `zava-store-ops-agent` | Foundry IQ AI Search (`zava-store-ops-kb`, filterable by `store_id`) | `store_id`                  |

## Containers

### `products` (partition key `/id`)

```jsonc
{
  "id": "ZV-PNT-001",
  "name": "Premium Interior Paint — Eggshell White",
  "category": "paint",
  "brand": "Zava Pro",
  "sku": "ZV-PNT-001",
  "price_usd": 32.99,
  "unit": "1 gallon",
  "description": "Low-VOC interior paint, dries in 1 hour, 400 sq ft coverage.",
  "tags": ["paint", "interior", "white", "low-voc"],
  "inventory_by_store": {
    "seattle": 45, "bellevue": 12, "tacoma": 28, "redmond": 7,
    "kirkland": 33, "spokane": 19, "everett": 14, "online": 220
  },
  "reorder_threshold": 15
}
```

### `campaigns` (partition key `/id`)

```jsonc
{
  "id": "ZV-CMP-2026-001",
  "name": "Spring Paint Sale 2026",
  "status": "active",
  "category": "paint",
  "start_date": "2026-04-01",
  "end_date": "2026-05-31",
  "stores": ["seattle", "bellevue", "tacoma", "online"],
  "featured_products": ["ZV-PNT-001", "ZV-PNT-002", "ZV-PNT-005"],
  "discount_percent": 20,
  "channel": ["in-store", "email", "social"],
  "target_audience": "DIY homeowners, weekend renovators",
  "budget_usd": 180000,
  "spend_usd": 62000,
  "impressions": 1850000,
  "clicks": 32000,
  "roi": null,
  "kb_brief": "ZV-CMP-2026-001_brief.md"
}
```

### Markdown KBs (Foundry IQ → Azure AI Search)

Every Markdown file in `src/knowledge_seed/store_ops/` and
`src/knowledge_seed/marketing/` carries YAML frontmatter that becomes
filterable fields on the AI Search index:

```yaml
---
title: Discount Approval Matrix
store_id: all          # or seattle, bellevue, ...
category_id: all       # marketing docs only
doc_type: policy       # policy | handbook | sop | brief | post_mortem
---
```

The `zava-store-ops-kb` index includes `store_id` as a **filterable** field
so the agent can scope retrieval to a single store.

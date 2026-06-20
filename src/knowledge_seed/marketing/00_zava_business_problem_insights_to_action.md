---
title: Zava — The Business Problem (Insights to Action)
campaign_id: null
category_id: all
store_id: all
doc_type: briefing
effective: 2026-03-01
owner: Leadership
---

# Zava — The Business Problem (Insights to Action)

> **Read this first.** It explains, in one page, the business problem this
> assistant solves: turning **insight** (what the data says) into **action**
> (what a store or marketing leader should do next).

## Who Zava is
Zava is a Pacific Northwest DIY hardware retailer — **7 stores** (Seattle,
Bellevue, Tacoma, Redmond, Kirkland, Spokane, Everett) and an **online**
fulfilment centre — selling across **8 categories** (paint, power-tools,
hand-tools, garden, lumber, electrical, plumbing, hardware).

## The problem
Zava already has the data. Sales, inventory and marketing each live in their
own system. **The gap is the join** — no single view answers a question that
spans all three, so promotional decisions are made late, by hand, after the
revenue is lost.

## The question this assistant answers
> *"Sales for our Spring Paint Sale in Seattle look soft — which products are
> low on stock, what did last year teach us, and what should the store manager
> do right now?"*

Answering it joins three domains on the same keys
(`store_id = "seattle"`, `category_id = "paint"`):

| Domain | Insight it contributes |
|--------|------------------------|
| **Sales** | Paint revenue at Seattle is trending down. |
| **Inventory** | `ZV-PNT-001` stock cover at Seattle is critically low. |
| **Marketing** | A 20%-off promo is live; last year's post-mortem warned this stockout would recur. |

## From insight to action
| Insight | Recommended action |
|---------|--------------------|
| Soft paint sales + critically low Seattle cover on `ZV-PNT-001` during an active promo. | Pre-position **200+ units** of `ZV-PNT-001` at Seattle before the next weekend. |
| Last year lost ~60 units / ~$1,800 to restock lag. | Auto-trigger restock when Seattle paint cover drops **below 30 units**. |
| The 2-for-$60 bundle drives an attach rate the forecast misses. | Raise the Seattle paint reorder threshold from **15 → 25** for Apr–May. |

## Why this needs agents, not a report
The answer changes weekly, spans three systems, and ends in a **decision under a
policy** (how much to restock, what discount a manager may approve). Specialist
agents gather the insight from each domain, and an **Action Recommender** turns
the joined picture into the recommendation above — with every claim sourced.

## Shared keys (so every agent joins cleanly)
- `store_id`: seattle, bellevue, tacoma, redmond, kirkland, spokane, everett, online
- `category_id`: paint, power-tools, hand-tools, garden, lumber, electrical, plumbing, hardware
- `product_id`: `ZV-<CAT>-NNN` — e.g. `ZV-PNT-001` (paint), `ZV-GDN-003`
  (garden), `ZV-PWT-006` (power-tools). **48 SKUs**, 6 per category.

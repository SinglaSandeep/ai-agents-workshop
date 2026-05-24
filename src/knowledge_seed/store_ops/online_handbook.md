---
title: Online Fulfillment Center — Operations Handbook
store_id: online
doc_type: handbook
effective: 2026-01-01
owner: Online Operations
---

# Online Fulfillment Center — Operations Handbook

**Location.** Auburn, WA distribution center.
**Hours.** 24/7 operations with three shifts.

## Role

The online fulfillment center (FC) services zava.com orders for the
entire Pacific Northwest. It also holds **deep safety stock** of the top
500 SKUs, so when a brick-and-mortar store goes low on a hot-promo item,
the inventory team can pull from `inventory_by_store.online` and ship
to the store overnight.

## Local discount-approval guidance

Online discount codes are managed by the marketing team, not the FC.
Customer-service goodwill credits up to **15%** may be issued by the
online customer-service supervisor without district approval. Anything
above goes through the chain Discount Approval Matrix.

## Shipping & returns

- Standard ground: 1–3 business days within Washington / Oregon.
- Expedited: next-day if ordered by 11 AM PT.
- Online returns: customer chooses ship-back (UPS label) or in-store drop.
  Any PNW store accepts online returns — see the chain Returns &
  Exchanges Policy.

## Safety

The FC follows the chain Safety Handbook plus warehouse-specific rules
including forklift / reach-truck certifications, pedestrian aisle marking,
and the conveyor lock-out / tag-out procedure documented in the FC
operations binder.

## Restock-to-store workflow

1. Store manager raises a "RestockReq" ticket noting SKU, qty, and
   urgency.
2. FC ships overnight if `inventory_by_store.online >= request qty + 50`.
3. If FC stock is insufficient, the merchant team is paged.

## Local contacts

- FC director: Alex Tran.
- District equivalent: VP Retail Operations.

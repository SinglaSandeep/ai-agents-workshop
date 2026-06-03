"""Deterministically generate Zava marketing campaign documents (>1000 rows).

The curated ``marketing_seed.json`` campaigns (with their FoundryIQ briefs)
are kept as-is; this generator *tops up* the dataset to >1000 campaigns so
the Marketing agent has rich Cosmos data to join against the knowledge base.

Generated campaigns reuse the shared store / category / SKU universe from
:mod:`src.common.zava_reference`, and span several years so the agent can
analyse historical performance. Reproducible (seeded).
"""

from __future__ import annotations

import random
from datetime import date, timedelta

from src.common.zava_reference import CATALOG, CATEGORIES, STORES

SEED = 20260605
TARGET_TOTAL = 1100

_CHANNELS = ["in-store", "email", "social", "search", "display"]
_AUDIENCES = [
    "DIY homeowners, weekend renovators",
    "Professional contractors and trades",
    "First-time homeowners",
    "Garden and outdoor enthusiasts",
    "Small business / facilities buyers",
    "Bargain hunters and clearance shoppers",
]
_THEMES = {
    "paint": ["Color Refresh", "Interior Makeover", "Paint & Save"],
    "power-tools": ["Pro Power Days", "Tool Upgrade", "Workshop Ready"],
    "hand-tools": ["Toolbox Essentials", "Grip & Go", "Everyday Carry"],
    "garden": ["Spring Grow", "Backyard Bloom", "Outdoor Living"],
    "lumber": ["Build Season", "Frame It", "Deck & Fence"],
    "electrical": ["Bright Ideas", "Wired Right", "Power Up"],
    "plumbing": ["Leak-Free", "Flow Pro", "Bath & Beyond"],
    "hardware": ["Fasten Fest", "Fix-It Days", "Hardware Haul"],
}
_STATUSES = ["completed", "completed", "completed", "active", "scheduled"]


def _existing_ids(curated: list[dict]) -> set[str]:
    return {c.get("id") for c in curated}


def generate_rows(curated: list[dict] | None = None, target_total: int = TARGET_TOTAL) -> list[dict]:
    """Return generated campaigns to ADD on top of the curated list.

    Pass the already-loaded curated campaigns so generated ids/years do not
    collide with them. Returns only the *new* synthetic campaigns.
    """
    curated = curated or []
    rng = random.Random(SEED)
    taken = _existing_ids(curated)
    by_category = {c: [p["id"] for p in CATALOG if p["category"] == c] for c in CATEGORIES}
    stores = list(STORES)

    needed = max(0, target_total - len(curated))
    rows: list[dict] = []
    seq_by_year: dict[int, int] = {}

    for _ in range(needed):
        year = rng.choice([2023, 2024, 2025, 2026])
        seq_by_year[year] = seq_by_year.get(year, 100) + 1
        cid = f"ZV-CMP-{year}-{seq_by_year[year]:03d}"
        while cid in taken:
            seq_by_year[year] += 1
            cid = f"ZV-CMP-{year}-{seq_by_year[year]:03d}"
        taken.add(cid)

        category = rng.choice(CATEGORIES)
        theme = rng.choice(_THEMES[category])
        start = date(year, rng.randint(1, 11), rng.randint(1, 28))
        end = start + timedelta(days=rng.choice([14, 21, 30, 45, 60]))
        status = rng.choice(_STATUSES)
        if end < date(2026, 5, 30):
            status = "completed"

        store_sample = rng.sample(stores, k=rng.randint(2, min(5, len(stores))))
        featured = rng.sample(by_category[category], k=min(rng.randint(2, 3), len(by_category[category])))
        channels = rng.sample(_CHANNELS, k=rng.randint(2, 4))

        budget = rng.choice([40000, 60000, 90000, 120000, 180000, 240000])
        spend = int(budget * rng.uniform(0.35, 1.0))
        impressions = rng.randint(200_000, 4_000_000)
        clicks = int(impressions * rng.uniform(0.006, 0.03))
        revenue = spend * rng.uniform(1.2, 4.5)
        roi = round((revenue - spend) / spend, 2) if spend else None

        rows.append(
            {
                "id": cid,
                "name": f"{theme} {year}",
                "status": status,
                "category": category,
                "start_date": start.isoformat(),
                "end_date": end.isoformat(),
                "stores": store_sample,
                "featured_products": featured,
                "discount_percent": rng.choice([10, 15, 20, 25, 30]),
                "channel": channels,
                "target_audience": rng.choice(_AUDIENCES),
                "budget_usd": budget,
                "spend_usd": spend,
                "impressions": impressions,
                "clicks": clicks,
                "roi": roi,
                "kb_brief": None,
            }
        )

    return rows


if __name__ == "__main__":  # pragma: no cover - quick local check
    data = generate_rows()
    print(f"generated {len(data)} synthetic campaigns; sample:")
    print(data[0])

"""Deterministically generate Zava sales order-line documents (>1000 rows).

The data is intentionally *shaped* so the Insights-to-Action workflow has
something to act on:

  * 12 months of history (rolling), so `monthly_trend` shows real movement.
  * A couple of categories trend UP (garden in spring) and a couple trend
    DOWN (paint cooling off) month over month.
  * Margin varies by customer segment (contractors buy at thinner margin).

Re-running is reproducible because the RNG is seeded.
"""

from __future__ import annotations

import random
from datetime import date, timedelta

from src.common.zava_reference import (
    CATALOG,
    CATEGORIES,
    CHANNELS,
    CUSTOMER_SEGMENTS,
    STORE_REGION,
    STORES,
)

SEED = 20260603
TARGET_ROWS = 1500
# 12 rolling months ending the month before "today" in the workshop timeline.
_END = date(2026, 5, 31)


def _month_list(n: int = 12) -> list[date]:
    months: list[date] = []
    y, m = _END.year, _END.month
    for _ in range(n):
        months.append(date(y, m, 1))
        m -= 1
        if m == 0:
            y -= 1
            m = 12
    return list(reversed(months))


# Category demand multiplier by month index (0..11). Values >1 boost volume.
def _seasonal_factor(category: str, month_idx: int, total_months: int) -> float:
    progress = month_idx / max(total_months - 1, 1)  # 0 -> 1 across the window
    if category == "garden":
        # Strong upward / spring ramp.
        return 0.6 + 1.2 * progress
    if category == "paint":
        # Gentle decline over the window.
        return 1.3 - 0.6 * progress
    if category == "power-tools":
        # Mild upward trend.
        return 0.85 + 0.4 * progress
    if category == "lumber":
        # Mid-window peak.
        return 1.0 + 0.5 * (1 - abs(progress - 0.5) * 2)
    return 1.0


def generate_rows(target: int = TARGET_ROWS) -> list[dict]:
    rng = random.Random(SEED)
    months = _month_list(12)
    by_category = {c: [p for p in CATALOG if p["category"] == c] for c in CATEGORIES}
    stores = [s for s in STORES]

    rows: list[dict] = []
    seq = 0
    # Distribute rows roughly evenly across months, weighted by seasonality.
    per_month = max(target // len(months), 1)

    for m_idx, first in enumerate(months):
        month_str = f"{first.year:04d}-{first.month:02d}"
        # Days in this month.
        if first.month == 12:
            nxt = date(first.year + 1, 1, 1)
        else:
            nxt = date(first.year, first.month + 1, 1)
        days_in_month = (nxt - first).days

        for _ in range(per_month + rng.randint(0, 6)):
            category = rng.choice(CATEGORIES)
            product = rng.choice(by_category[category])
            store = rng.choice(stores)
            region = STORE_REGION[store]
            channel = "online" if store == "online" else rng.choice(CHANNELS)
            segment = rng.choices(CUSTOMER_SEGMENTS, weights=[5, 3, 2])[0]

            factor = _seasonal_factor(category, m_idx, len(months))
            base_units = rng.randint(1, 14)
            units = max(1, int(round(base_units * factor)))

            unit_price = product["price_usd"]
            # Contractors/pros get a small volume discount.
            discount = {"diy": 0.0, "pro": 0.04, "contractor": 0.08}[segment]
            eff_price = round(unit_price * (1 - discount), 2)
            revenue = round(eff_price * units, 2)
            cost = round(product["unit_cost_usd"] * units, 2)
            margin = round(revenue - cost, 2)

            seq += 1
            order_day = rng.randint(1, days_in_month)
            order_date = first + timedelta(days=order_day - 1)
            order_id = f"ZV-SO-{first.year:04d}-{seq:06d}"

            rows.append(
                {
                    "id": order_id,
                    "order_date": order_date.isoformat(),
                    "month": month_str,
                    "store_id": store,
                    "region": region,
                    "channel": channel,
                    "category": category,
                    "product_id": product["id"],
                    "product_name": product["name"],
                    "customer_segment": segment,
                    "units": units,
                    "unit_price_usd": eff_price,
                    "revenue_usd": revenue,
                    "cost_usd": cost,
                    "margin_usd": margin,
                }
            )

    return rows


if __name__ == "__main__":  # pragma: no cover - quick local check
    data = generate_rows()
    print(f"generated {len(data)} sales rows; sample:")
    print(data[0])

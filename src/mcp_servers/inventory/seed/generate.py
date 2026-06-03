"""Deterministically generate Zava distributor inventory snapshots (>1000 rows).

Every (warehouse × product) pair gets 6 weekly snapshots so the workflow can
look at *current* stock health (``is_latest = true``) and at a short trend via
``inventory_trend``. The data is shaped so there are clear low-stock,
stockout and overstock cases for the Insights-to-Action workflow to act on.

6 warehouses × 40 products × 6 weeks = 1440 documents. Reproducible (seeded).
"""

from __future__ import annotations

import random
from datetime import date, timedelta

from src.common.zava_reference import CATALOG, DISTRIBUTORS

SEED = 20260604
WEEKS = 6
# Snapshots are taken on Saturdays; the latest is the Saturday on/before _END.
_END = date(2026, 5, 30)


def _week_dates(n: int = WEEKS) -> list[date]:
    """Return ``n`` weekly snapshot dates, oldest first, ending at ``_END``."""
    return [_END - timedelta(days=7 * (n - 1 - i)) for i in range(n)]


def _iso_week(d: date) -> str:
    iso = d.isocalendar()
    return f"{iso.year:04d}-W{iso.week:02d}"


def _status(available: int, reorder_point: int, max_stock: int) -> str:
    if available <= 0:
        return "stockout"
    if available <= reorder_point:
        return "low"
    if available > max_stock:
        return "overstock"
    return "healthy"


def generate_rows() -> list[dict]:
    rng = random.Random(SEED)
    weeks = _week_dates()
    rows: list[dict] = []

    for dist in DISTRIBUTORS:
        for warehouse in dist["warehouses"]:
            for product in CATALOG:
                # Per (warehouse, product) baseline characteristics.
                weekly_demand = rng.randint(8, 70)
                lead_time = rng.choice([5, 7, 10, 14])
                safety_stock = int(weekly_demand * rng.uniform(0.8, 1.5))
                reorder_point = safety_stock + int(weekly_demand * (lead_time / 7))
                max_stock = reorder_point + weekly_demand * rng.randint(3, 6)

                # Choose a "fate" so the dataset has actionable extremes.
                fate = rng.choices(
                    ["healthy", "draining", "overstock", "stockout"],
                    weights=[6, 3, 2, 1],
                )[0]
                if fate == "overstock":
                    on_hand = int(max_stock * rng.uniform(1.1, 1.6))
                elif fate == "stockout":
                    on_hand = int(reorder_point * rng.uniform(1.0, 1.8))
                elif fate == "draining":
                    on_hand = int(max_stock * rng.uniform(0.7, 1.0))
                else:
                    on_hand = int(rng.uniform(reorder_point + 1, max_stock))

                for w_idx, snap in enumerate(weeks):
                    # Weekly drift: draining/stockout fates lose stock over time.
                    if fate in ("draining", "stockout"):
                        consume = int(weekly_demand * rng.uniform(0.9, 1.6))
                        on_hand = max(0, on_hand - consume)
                    elif fate == "overstock":
                        on_hand = max(0, on_hand - int(weekly_demand * rng.uniform(0.2, 0.6)))
                    else:
                        # Healthy lines are replenished and wobble around the band.
                        drift = int(weekly_demand * rng.uniform(-0.5, 0.6))
                        on_hand = max(0, min(max_stock, on_hand - drift))

                    allocated = min(on_hand, int(weekly_demand * rng.uniform(0.1, 0.6)))
                    available = max(0, on_hand - allocated)
                    weeks_of_cover = round(available / weekly_demand, 1) if weekly_demand else 0.0
                    status = _status(available, reorder_point, max_stock)
                    is_latest = w_idx == len(weeks) - 1
                    inv_id = (
                        f"ZV-INV-{warehouse}-{product['id']}-{snap.strftime('%Y%m%d')}"
                    )

                    rows.append(
                        {
                            "id": inv_id,
                            "snapshot_date": snap.isoformat(),
                            "week": _iso_week(snap),
                            "distributor_id": dist["distributor_id"],
                            "distributor_name": dist["distributor_name"],
                            "warehouse_id": warehouse,
                            "region": dist["region"],
                            "product_id": product["id"],
                            "product_name": product["name"],
                            "category": product["category"],
                            "on_hand_units": on_hand,
                            "allocated_units": allocated,
                            "available_units": available,
                            "reorder_point": reorder_point,
                            "safety_stock": safety_stock,
                            "max_stock": max_stock,
                            "lead_time_days": lead_time,
                            "weekly_demand_units": weekly_demand,
                            "weeks_of_cover": weeks_of_cover,
                            "stock_status": status,
                            "is_latest": is_latest,
                        }
                    )

    return rows


if __name__ == "__main__":  # pragma: no cover - quick local check
    data = generate_rows()
    print(f"generated {len(data)} inventory snapshots; sample:")
    print(data[-1])

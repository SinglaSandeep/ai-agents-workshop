"""Read-only Cosmos DB repository for Zava distributor inventory snapshots.

Every Cosmos query is logged at INFO on the ``zava.mcp.inventory.cosmos``
logger, mirroring the sales/marketing repositories so the same OpenTelemetry
pipeline picks up query traces.

The container holds one document per *(distributor warehouse × product ×
weekly snapshot)*. The most recent snapshot for each warehouse/product is
flagged ``is_latest = true``; "current state" tools filter on that flag, while
``inventory_trend`` walks the full weekly history.
"""

from __future__ import annotations

import logging
import time
from typing import Any

from src.common.cosmos import get_container
from src.common.settings import get_settings

logger = logging.getLogger("zava.mcp.inventory.cosmos")

# Whitelisted GROUP BY dimensions. The value is interpolated into the SQL
# (Cosmos cannot parameterise an identifier), so it MUST come from this
# trusted set — never from raw user input — to avoid SQL injection.
_GROUP_DIMENSIONS = {
    "distributor_id": "c.distributor_id",
    "distributor_name": "c.distributor_name",
    "warehouse_id": "c.warehouse_id",
    "region": "c.region",
    "category": "c.category",
    "stock_status": "c.stock_status",
}

_STATUS_VALUES = ("healthy", "low", "overstock", "stockout")


def _log_query(op: str, query: str, params: list[dict[str, Any]] | None, *, count: int, elapsed_ms: float) -> None:
    logger.info(
        "cosmos %s rows=%d elapsed_ms=%.1f query=%s params=%s",
        op,
        count,
        elapsed_ms,
        " ".join(query.split()),
        params or [],
    )


class InventoryRepository:
    def __init__(self) -> None:
        settings = get_settings()
        self._container = get_container(settings.cosmos_inventory_container)

    def _query(self, op: str, query: str, params: list[dict[str, Any]] | None = None) -> list[dict[str, Any]]:
        t0 = time.perf_counter()
        rows = list(
            self._container.query_items(
                query=query, parameters=params, enable_cross_partition_query=True
            )
        )
        _log_query(op, query, params, count=len(rows), elapsed_ms=(time.perf_counter() - t0) * 1000)
        return rows

    def list_distributors(self) -> list[dict[str, Any]]:
        """Return each distributor with its warehouses and region (latest snapshot)."""
        rows = self._query(
            "list_distributors",
            "SELECT DISTINCT c.distributor_id, c.distributor_name, c.region, c.warehouse_id "
            "FROM c WHERE c.is_latest = true",
        )
        grouped: dict[str, dict[str, Any]] = {}
        for r in rows:
            d = grouped.setdefault(
                r["distributor_id"],
                {
                    "distributor_id": r["distributor_id"],
                    "distributor_name": r.get("distributor_name"),
                    "region": r.get("region"),
                    "warehouses": set(),
                },
            )
            if r.get("warehouse_id"):
                d["warehouses"].add(r["warehouse_id"])
        return [
            {**d, "warehouses": sorted(d["warehouses"])}
            for d in sorted(grouped.values(), key=lambda x: x["distributor_id"])
        ]

    def stock_status_summary(self, region: str | None = None) -> list[dict[str, Any]]:
        """Count latest-snapshot SKUs by stock_status (healthy/low/overstock/stockout)."""
        where = ["c.is_latest = true"]
        params: list[dict[str, Any]] = []
        if region:
            where.append("LOWER(c.region) = LOWER(@region)")
            params.append({"name": "@region", "value": region})
        clause = " AND ".join(where)
        # Cosmos rejects multi-aggregate cross-partition GROUP BY on this
        # account, so we project the raw columns and aggregate in Python.
        rows = self._query(
            "stock_status_summary",
            "SELECT c.stock_status AS stock_status, c.available_units AS available_units "
            f"FROM c WHERE {clause}",
            params or None,
        )
        agg: dict[Any, dict[str, Any]] = {}
        for r in rows:
            key = r.get("stock_status")
            a = agg.setdefault(key, {"stock_status": key, "skus": 0, "available_units": 0})
            a["skus"] += 1
            a["available_units"] += r.get("available_units") or 0
        result = list(agg.values())
        result.sort(key=lambda r: r.get("skus", 0), reverse=True)
        return result

    def low_stock(self, region: str | None = None, warehouse_id: str | None = None, limit: int = 25) -> list[dict[str, Any]]:
        """Latest SKUs at or below their reorder point (low or stockout), worst first."""
        where = ["c.is_latest = true", "c.available_units <= c.reorder_point"]
        params: list[dict[str, Any]] = []
        if region:
            where.append("LOWER(c.region) = LOWER(@region)")
            params.append({"name": "@region", "value": region})
        if warehouse_id:
            where.append("LOWER(c.warehouse_id) = LOWER(@wh)")
            params.append({"name": "@wh", "value": warehouse_id})
        clause = " AND ".join(where)
        rows = self._query(
            "low_stock",
            f"SELECT * FROM c WHERE {clause}",
            params or None,
        )
        rows.sort(key=lambda r: r.get("weeks_of_cover", 0))
        return [self._project(r) for r in rows[:limit]]

    def overstock(self, limit: int = 25) -> list[dict[str, Any]]:
        """Latest SKUs flagged overstock (above max_stock), most excess first."""
        rows = self._query(
            "overstock",
            "SELECT * FROM c WHERE c.is_latest = true AND c.stock_status = 'overstock'",
        )
        rows.sort(key=lambda r: r.get("on_hand_units", 0) - r.get("max_stock", 0), reverse=True)
        return [self._project(r) for r in rows[:limit]]

    def reorder_recommendations(self, limit: int = 25) -> list[dict[str, Any]]:
        """Latest low/stockout SKUs with a suggested reorder quantity to reach max_stock."""
        rows = self._query(
            "reorder_recommendations",
            "SELECT * FROM c WHERE c.is_latest = true "
            "AND c.available_units <= c.reorder_point",
        )
        recs: list[dict[str, Any]] = []
        for r in rows:
            suggested = max(0, int(r.get("max_stock", 0)) - int(r.get("available_units", 0)))
            recs.append(
                {
                    **self._project(r),
                    "suggested_reorder_units": suggested,
                    "lead_time_days": r.get("lead_time_days"),
                }
            )
        recs.sort(key=lambda r: r.get("weeks_of_cover", 0))
        return recs[:limit]

    def inventory_for_product(self, product_id: str) -> dict[str, Any] | None:
        """Latest inventory for one product across all warehouses, plus aggregate cover."""
        params = [{"name": "@pid", "value": product_id}]
        rows = self._query(
            "inventory_for_product",
            "SELECT * FROM c WHERE c.is_latest = true AND c.product_id = @pid",
            params,
        )
        if not rows:
            return None
        on_hand = sum(int(r.get("on_hand_units", 0)) for r in rows)
        available = sum(int(r.get("available_units", 0)) for r in rows)
        weekly_demand = sum(float(r.get("weekly_demand_units", 0)) for r in rows)
        weeks_of_cover = round(available / weekly_demand, 1) if weekly_demand else None
        return {
            "product_id": product_id,
            "product_name": rows[0].get("product_name"),
            "category": rows[0].get("category"),
            "total_on_hand_units": on_hand,
            "total_available_units": available,
            "total_weekly_demand_units": round(weekly_demand, 1),
            "weeks_of_cover": weeks_of_cover,
            "by_warehouse": [self._project(r) for r in rows],
        }

    def inventory_trend(self, warehouse_id: str, product_id: str) -> list[dict[str, Any]]:
        """Weekly available-units / weeks-of-cover history for one warehouse + product."""
        params = [
            {"name": "@wh", "value": warehouse_id},
            {"name": "@pid", "value": product_id},
        ]
        rows = self._query(
            "inventory_trend",
            "SELECT c.snapshot_date, c.week, c.on_hand_units, c.available_units, "
            "c.weekly_demand_units, c.weeks_of_cover, c.stock_status "
            "FROM c WHERE LOWER(c.warehouse_id) = LOWER(@wh) AND c.product_id = @pid",
            params,
        )
        rows.sort(key=lambda r: r.get("snapshot_date", ""))
        return rows

    def get_inventory(self, inventory_id: str) -> dict[str, Any] | None:
        t0 = time.perf_counter()
        try:
            item = self._container.read_item(item=inventory_id, partition_key=inventory_id)
            logger.info(
                "cosmos get_inventory id=%s found=True elapsed_ms=%.1f",
                inventory_id,
                (time.perf_counter() - t0) * 1000,
            )
            return item
        except Exception as exc:
            logger.info(
                "cosmos get_inventory id=%s found=False elapsed_ms=%.1f error=%s",
                inventory_id,
                (time.perf_counter() - t0) * 1000,
                exc.__class__.__name__,
            )
            return None

    @staticmethod
    def _project(row: dict[str, Any]) -> dict[str, Any]:
        """Trim a raw snapshot document to the fields agents care about."""
        keys = (
            "id",
            "snapshot_date",
            "week",
            "distributor_id",
            "distributor_name",
            "warehouse_id",
            "region",
            "product_id",
            "product_name",
            "category",
            "on_hand_units",
            "allocated_units",
            "available_units",
            "reorder_point",
            "safety_stock",
            "max_stock",
            "weekly_demand_units",
            "weeks_of_cover",
            "stock_status",
        )
        return {k: row.get(k) for k in keys}

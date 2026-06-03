"""Read-only Cosmos DB repository for Zava sales transactions.

Every Cosmos query is logged at INFO on the ``zava.mcp.sales.cosmos`` logger,
mirroring the products/marketing repositories so the same OpenTelemetry
pipeline picks up query traces.

The container holds one document per *order line* (a single product sold in a
single transaction). Aggregations (revenue/units/margin) are pushed down to
Cosmos with ``GROUP BY`` where possible so the agent gets pre-summarised
insight rows rather than thousands of raw lines.
"""

from __future__ import annotations

import logging
import time
from typing import Any

from src.common.cosmos import get_container
from src.common.settings import get_settings

logger = logging.getLogger("zava.mcp.sales.cosmos")

# Whitelisted GROUP BY dimensions. The value is interpolated into the SQL
# (Cosmos cannot parameterise an identifier), so it MUST come from this
# trusted set — never from raw user input — to avoid SQL injection.
_GROUP_DIMENSIONS = {
    "store_id": "c.store_id",
    "region": "c.region",
    "category": "c.category",
    "channel": "c.channel",
    "customer_segment": "c.customer_segment",
    "month": "c.month",
    "product_id": "c.product_id",
}


def _log_query(op: str, query: str, params: list[dict[str, Any]] | None, *, count: int, elapsed_ms: float) -> None:
    logger.info(
        "cosmos %s rows=%d elapsed_ms=%.1f query=%s params=%s",
        op,
        count,
        elapsed_ms,
        " ".join(query.split()),
        params or [],
    )


class SalesRepository:
    def __init__(self) -> None:
        settings = get_settings()
        self._container = get_container(settings.cosmos_sales_container)

    def _query(self, op: str, query: str, params: list[dict[str, Any]] | None = None) -> list[dict[str, Any]]:
        t0 = time.perf_counter()
        rows = list(
            self._container.query_items(
                query=query, parameters=params, enable_cross_partition_query=True
            )
        )
        _log_query(op, query, params, count=len(rows), elapsed_ms=(time.perf_counter() - t0) * 1000)
        return rows

    def list_dimensions(self) -> dict[str, list[str]]:
        """Return the distinct stores, regions, categories, channels and months."""
        return {
            "stores": self._query("dim_stores", "SELECT DISTINCT VALUE c.store_id FROM c"),
            "regions": self._query("dim_regions", "SELECT DISTINCT VALUE c.region FROM c"),
            "categories": self._query("dim_categories", "SELECT DISTINCT VALUE c.category FROM c"),
            "channels": self._query("dim_channels", "SELECT DISTINCT VALUE c.channel FROM c"),
            "months": sorted(self._query("dim_months", "SELECT DISTINCT VALUE c.month FROM c")),
            "customer_segments": self._query(
                "dim_segments", "SELECT DISTINCT VALUE c.customer_segment FROM c"
            ),
        }

    def revenue_summary(self, group_by: str = "category", limit: int = 50) -> list[dict[str, Any]]:
        """Aggregate revenue, units and margin grouped by a whitelisted dimension."""
        field = _GROUP_DIMENSIONS.get(group_by)
        if field is None:
            raise ValueError(
                f"Unsupported group_by '{group_by}'. Choose one of {sorted(_GROUP_DIMENSIONS)}."
            )
        # Cosmos rejects multi-aggregate cross-partition GROUP BY on this
        # account, so we project the raw columns and aggregate in Python.
        rows = self._query(
            "revenue_summary",
            f"SELECT {field} AS dimension, c.revenue_usd AS revenue_usd, "
            "c.units AS units, c.margin_usd AS margin_usd FROM c",
        )
        agg: dict[Any, dict[str, Any]] = {}
        for r in rows:
            key = r.get("dimension")
            a = agg.setdefault(
                key,
                {"dimension": key, "revenue_usd": 0.0, "units": 0, "margin_usd": 0.0, "orders": 0},
            )
            a["revenue_usd"] += r.get("revenue_usd") or 0
            a["units"] += r.get("units") or 0
            a["margin_usd"] += r.get("margin_usd") or 0
            a["orders"] += 1
        result = list(agg.values())
        for a in result:
            a["revenue_usd"] = round(a["revenue_usd"], 2)
            a["margin_usd"] = round(a["margin_usd"], 2)
        result.sort(key=lambda r: r["revenue_usd"], reverse=True)
        return result[:limit]

    def monthly_trend(self, category: str | None = None, store_id: str | None = None) -> list[dict[str, Any]]:
        """Return revenue/units/margin per month, optionally filtered by category/store.

        Use this to spot rising or falling demand — the core signal the
        insights-to-action workflow acts on.
        """
        where: list[str] = []
        params: list[dict[str, Any]] = []
        if category:
            where.append("LOWER(c.category) = LOWER(@cat)")
            params.append({"name": "@cat", "value": category})
        if store_id:
            where.append("LOWER(c.store_id) = LOWER(@store)")
            params.append({"name": "@store", "value": store_id})
        clause = (" WHERE " + " AND ".join(where)) if where else ""
        rows = self._query(
            "monthly_trend",
            "SELECT c.month AS month, c.revenue_usd AS revenue_usd, "
            f"c.units AS units, c.margin_usd AS margin_usd FROM c{clause}",
            params or None,
        )
        agg: dict[Any, dict[str, Any]] = {}
        for r in rows:
            key = r.get("month")
            a = agg.setdefault(
                key, {"month": key, "revenue_usd": 0.0, "units": 0, "margin_usd": 0.0}
            )
            a["revenue_usd"] += r.get("revenue_usd") or 0
            a["units"] += r.get("units") or 0
            a["margin_usd"] += r.get("margin_usd") or 0
        result = list(agg.values())
        for a in result:
            a["revenue_usd"] = round(a["revenue_usd"], 2)
            a["margin_usd"] = round(a["margin_usd"], 2)
        result.sort(key=lambda r: r.get("month", ""))
        return result

    def top_products(self, metric: str = "revenue_usd", limit: int = 10, ascending: bool = False) -> list[dict[str, Any]]:
        """Rank products by total revenue or units.

        Pass ``ascending=True`` to surface the worst performers (candidates
        for a markdown / re-engagement action).
        """
        metric = metric if metric in ("revenue_usd", "units", "margin_usd") else "revenue_usd"
        rows = self._query(
            "top_products",
            "SELECT c.product_id AS product_id, c.product_name AS product_name, "
            "c.category AS category, c.revenue_usd AS revenue_usd, "
            "c.units AS units, c.margin_usd AS margin_usd FROM c",
        )
        agg: dict[Any, dict[str, Any]] = {}
        for r in rows:
            key = r.get("product_id")
            a = agg.setdefault(
                key,
                {
                    "product_id": key,
                    "product_name": r.get("product_name"),
                    "category": r.get("category"),
                    "revenue_usd": 0.0,
                    "units": 0,
                    "margin_usd": 0.0,
                },
            )
            a["revenue_usd"] += r.get("revenue_usd") or 0
            a["units"] += r.get("units") or 0
            a["margin_usd"] += r.get("margin_usd") or 0
        result = list(agg.values())
        for a in result:
            a["revenue_usd"] = round(a["revenue_usd"], 2)
            a["margin_usd"] = round(a["margin_usd"], 2)
        result.sort(key=lambda r: r.get(metric, 0), reverse=not ascending)
        return result[:limit]

    def sales_for_product(self, product_id: str) -> dict[str, Any] | None:
        """Total revenue/units/margin for a single product plus its per-region split."""
        params = [{"name": "@pid", "value": product_id}]
        rows = self._query(
            "sales_for_product",
            "SELECT c.product_id AS product_id, c.product_name AS product_name, "
            "c.category AS category, c.region AS region, c.revenue_usd AS revenue_usd, "
            "c.units AS units, c.margin_usd AS margin_usd "
            "FROM c WHERE c.product_id = @pid",
            params,
        )
        if not rows:
            return None
        result: dict[str, Any] = {
            "product_id": product_id,
            "product_name": rows[0].get("product_name"),
            "category": rows[0].get("category"),
            "revenue_usd": 0.0,
            "units": 0,
            "margin_usd": 0.0,
        }
        regions: dict[Any, dict[str, Any]] = {}
        for r in rows:
            result["revenue_usd"] += r.get("revenue_usd") or 0
            result["units"] += r.get("units") or 0
            result["margin_usd"] += r.get("margin_usd") or 0
            reg = regions.setdefault(
                r.get("region"), {"region": r.get("region"), "revenue_usd": 0.0, "units": 0}
            )
            reg["revenue_usd"] += r.get("revenue_usd") or 0
            reg["units"] += r.get("units") or 0
        result["revenue_usd"] = round(result["revenue_usd"], 2)
        result["margin_usd"] = round(result["margin_usd"], 2)
        result["by_region"] = [
            {"region": v["region"], "revenue_usd": round(v["revenue_usd"], 2), "units": v["units"]}
            for v in regions.values()
        ]
        return result

    def get_order(self, order_id: str) -> dict[str, Any] | None:
        t0 = time.perf_counter()
        try:
            item = self._container.read_item(item=order_id, partition_key=order_id)
            logger.info("cosmos get_order id=%s found=True elapsed_ms=%.1f", order_id, (time.perf_counter() - t0) * 1000)
            return item
        except Exception as exc:
            logger.info(
                "cosmos get_order id=%s found=False elapsed_ms=%.1f error=%s",
                order_id,
                (time.perf_counter() - t0) * 1000,
                exc.__class__.__name__,
            )
            return None

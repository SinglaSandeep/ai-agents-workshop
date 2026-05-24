"""Read-only Cosmos DB repository for the Zava products catalog.

Every query executed against Cosmos is logged at INFO level on the
``zava.mcp.products.cosmos`` logger. Uvicorn forwards stdlib logging to the
console by default, so you will see one line per tool call when running the
server locally. Configure your aggregation / OpenTelemetry exporter against
that logger name to pipe these queries to App Insights.
"""

from __future__ import annotations

import logging
import time
from typing import Any

from src.common.cosmos import get_container
from src.common.settings import get_settings

logger = logging.getLogger("zava.mcp.products.cosmos")


def _log_query(op: str, query: str, params: list[dict[str, Any]] | None, *, count: int, elapsed_ms: float) -> None:
    """Emit one structured log line per Cosmos query."""
    logger.info(
        "cosmos %s rows=%d elapsed_ms=%.1f query=%s params=%s",
        op,
        count,
        elapsed_ms,
        " ".join(query.split()),
        params or [],
    )


class ProductsRepository:
    def __init__(self) -> None:
        settings = get_settings()
        self._container = get_container(settings.cosmos_products_container)

    def list_categories(self) -> list[str]:
        query = "SELECT DISTINCT VALUE c.category FROM c"
        t0 = time.perf_counter()
        rows = list(self._container.query_items(query=query, enable_cross_partition_query=True))
        _log_query("list_categories", query, None, count=len(rows), elapsed_ms=(time.perf_counter() - t0) * 1000)
        return rows

    def list_products(self, category: str | None = None, limit: int = 20) -> list[dict[str, Any]]:
        if category:
            query = (
                "SELECT TOP @limit c.id, c.name, c.category, c.brand, c.sku, c.unit, "
                "c.description, c.price_usd, c.tags FROM c WHERE LOWER(c.category) = LOWER(@cat)"
            )
            params = [{"name": "@limit", "value": limit}, {"name": "@cat", "value": category}]
        else:
            query = (
                "SELECT TOP @limit c.id, c.name, c.category, c.brand, c.sku, c.unit, "
                "c.description, c.price_usd, c.tags FROM c"
            )
            params = [{"name": "@limit", "value": limit}]
        t0 = time.perf_counter()
        rows = list(
            self._container.query_items(
                query=query, parameters=params, enable_cross_partition_query=True
            )
        )
        _log_query("list_products", query, params, count=len(rows), elapsed_ms=(time.perf_counter() - t0) * 1000)
        return rows

    def get_product(self, product_id: str) -> dict[str, Any] | None:
        t0 = time.perf_counter()
        try:
            item = self._container.read_item(item=product_id, partition_key=product_id)
            logger.info(
                "cosmos get_product id=%s found=True elapsed_ms=%.1f",
                product_id,
                (time.perf_counter() - t0) * 1000,
            )
            return item
        except Exception as exc:
            logger.info(
                "cosmos get_product id=%s found=False elapsed_ms=%.1f error=%s",
                product_id,
                (time.perf_counter() - t0) * 1000,
                exc.__class__.__name__,
            )
            return None

    def search_products(self, text: str, limit: int = 10) -> list[dict[str, Any]]:
        query = (
            "SELECT TOP @limit c.id, c.name, c.category, c.brand, c.sku, c.unit, "
            "c.description, c.price_usd, c.tags FROM c "
            "WHERE CONTAINS(LOWER(c.name), LOWER(@q)) "
            "   OR CONTAINS(LOWER(c.description), LOWER(@q)) "
            "   OR CONTAINS(LOWER(c.brand), LOWER(@q))"
        )
        params = [{"name": "@limit", "value": limit}, {"name": "@q", "value": text}]
        t0 = time.perf_counter()
        rows = list(
            self._container.query_items(
                query=query, parameters=params, enable_cross_partition_query=True
            )
        )
        _log_query("search_products", query, params, count=len(rows), elapsed_ms=(time.perf_counter() - t0) * 1000)
        return rows

    def inventory_by_store(self, product_id: str) -> dict[str, Any] | None:
        """Return the per-store inventory map for a single product."""
        product = self.get_product(product_id)
        if not product:
            return None
        return {
            "id": product["id"],
            "name": product.get("name"),
            "category": product.get("category"),
            "reorder_threshold": product.get("reorder_threshold"),
            "inventory_by_store": product.get("inventory_by_store", {}),
        }

    def low_stock_alerts(self, store_id: str, limit: int = 50) -> list[dict[str, Any]]:
        """List products at ``store_id`` whose on-hand stock is at or below their reorder threshold.

        Cosmos can't index a string-keyed nested object, so we read all docs and
        filter in-process — fine for workshop-sized data (sub-100 SKUs).
        """
        query = "SELECT c.id, c.name, c.category, c.reorder_threshold, c.inventory_by_store FROM c"
        t0 = time.perf_counter()
        rows = list(self._container.query_items(query=query, enable_cross_partition_query=True))
        store_id = store_id.lower()
        alerts: list[dict[str, Any]] = []
        for r in rows:
            inv = r.get("inventory_by_store") or {}
            on_hand = inv.get(store_id)
            if on_hand is None:
                continue
            threshold = r.get("reorder_threshold", 15)
            if on_hand <= threshold:
                alerts.append(
                    {
                        "id": r["id"],
                        "name": r.get("name"),
                        "category": r.get("category"),
                        "store_id": store_id,
                        "on_hand": on_hand,
                        "reorder_threshold": threshold,
                    }
                )
        alerts.sort(key=lambda a: (a["on_hand"], a["id"]))
        alerts = alerts[:limit]
        _log_query(
            "low_stock_alerts",
            query,
            [{"name": "@store_id", "value": store_id}],
            count=len(alerts),
            elapsed_ms=(time.perf_counter() - t0) * 1000,
        )
        return alerts

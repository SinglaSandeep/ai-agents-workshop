"""Read-only Cosmos DB repository for the Pepsico products catalog.

Every query executed against Cosmos is logged at INFO level on the
``pepsico.mcp.products.cosmos`` logger. Uvicorn forwards stdlib logging
to the console by default, so you will see one line per tool call when
running the server locally. Configure your aggregation / OpenTelemetry
exporter against that logger name to pipe these queries to App Insights.
"""

from __future__ import annotations

import logging
import time
from typing import Any

from src.common.cosmos import get_container
from src.common.settings import get_settings

logger = logging.getLogger("pepsico.mcp.products.cosmos")


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
                "SELECT TOP @limit c.id, c.name, c.category, c.brand, c.size, "
                "c.description, c.calories, c.price_usd FROM c WHERE LOWER(c.category) = LOWER(@cat)"
            )
            params = [{"name": "@limit", "value": limit}, {"name": "@cat", "value": category}]
        else:
            query = (
                "SELECT TOP @limit c.id, c.name, c.category, c.brand, c.size, "
                "c.description, c.calories, c.price_usd FROM c"
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
            "SELECT TOP @limit c.id, c.name, c.category, c.brand, c.size, "
            "c.description, c.calories, c.price_usd FROM c "
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

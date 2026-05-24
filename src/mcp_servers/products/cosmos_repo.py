"""Read-only Cosmos DB repository for the Zava products catalog.

You implement this file in **Exercise 02 / Task 02.02**. Every method should
return plain Python ``dict``s so the MCP server can JSON-serialise the result
straight back to the caller.

**Observability requirement.** Log every Cosmos query (op name, query text,
parameters, row count, elapsed ms) at ``INFO`` on the
``zava.mcp.products.cosmos`` logger so we can audit what the agent asks
for. See the reference solution for the exact helper.

Reference solution: ``solution/mcp_servers/products/cosmos_repo.py``.
"""

from __future__ import annotations

import logging
import time
from typing import Any

from src.common.cosmos import get_container
from src.common.settings import get_settings

logger = logging.getLogger("zava.mcp.products.cosmos")


def _log_query(
    op: str,
    query: str,
    params: list[dict[str, Any]] | None,
    *,
    count: int,
    elapsed_ms: float,
) -> None:
    """Emit one structured log line per Cosmos query.

    TODO (Exercise 02): call this helper at the end of every method below
    so each tool invocation produces an audit line on the
    ``zava.mcp.products.cosmos`` logger.
    """

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
        """Return every distinct ``c.category`` value in the products container.

        Zava categories are short ids like ``paint``, ``power-tools``,
        ``hardware``.
        """

        # TODO (Exercise 02): run a `SELECT DISTINCT VALUE c.category FROM c`
        # query, time it with `time.perf_counter()`, call `_log_query(...)`,
        # then return the list.
        raise NotImplementedError

    def list_products(self, category: str | None = None, limit: int = 20) -> list[dict[str, Any]]:
        """Return up to ``limit`` products, optionally filtered by ``category``."""

        # TODO (Exercise 02): SELECT TOP @limit ... with an optional WHERE
        # filter when `category` is provided. Log via `_log_query(...)`.
        raise NotImplementedError

    def get_product(self, product_id: str) -> dict[str, Any] | None:
        """Return one product by id (e.g. ``ZV-PNT-001``), or ``None`` if missing."""

        # TODO (Exercise 02): call `self._container.read_item(...)` and
        # return `None` on failure. Emit `logger.info(...)` with the id and
        # whether the item was found.
        raise NotImplementedError

    def search_products(self, text: str, limit: int = 10) -> list[dict[str, Any]]:
        """Free-text CONTAINS search across product name, brand, and description."""

        # TODO (Exercise 02): SELECT TOP @limit ... WHERE CONTAINS(LOWER(...)).
        # Log via `_log_query(...)`.
        raise NotImplementedError

    def inventory_by_store(self, product_id: str) -> dict[str, Any] | None:
        """Return the per-store inventory map for one product.

        Each product document has an ``inventory_by_store`` field shaped like
        ``{"seattle": 45, "bellevue": 12, ...}`` plus a ``reorder_threshold``.
        Return both, alongside the product id and name.
        """

        # TODO (Exercise 02): call `self.get_product(...)` and reshape the
        # result. Return None if the product is missing.
        raise NotImplementedError

    def low_stock_alerts(self, store_id: str, limit: int = 50) -> list[dict[str, Any]]:
        """Products at ``store_id`` whose on-hand stock is at or below the reorder threshold.

        Cosmos can't index a string-keyed nested object, so read all docs and
        filter in-process — fine for workshop-sized data (sub-100 SKUs).
        """

        # TODO (Exercise 02): query all docs, filter where
        # `inventory_by_store[store_id] <= reorder_threshold`, sort ascending
        # by on-hand, cap at `limit`.
        raise NotImplementedError

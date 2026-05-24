"""Read-only Cosmos DB repository for the Pepsico products catalog.

You implement this file in **Exercise 02 / Task 02.02**. Every method should
return plain Python ``dict``s so the MCP server can JSON-serialise the result
straight back to the caller.

**Observability requirement.** Log every Cosmos query (op name, query text,
parameters, row count, elapsed ms) at ``INFO`` on the
``pepsico.mcp.products.cosmos`` logger so we can audit what the agent asks
for. See the reference solution for the exact helper.

Reference solution: ``solution/mcp_servers/products/cosmos_repo.py``.
"""

from __future__ import annotations

import logging
import time
from typing import Any

from src.common.cosmos import get_container
from src.common.settings import get_settings

logger = logging.getLogger("pepsico.mcp.products.cosmos")


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
    ``pepsico.mcp.products.cosmos`` logger.
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
        """Return every distinct ``c.category`` value in the products container."""

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
        """Return a single product by id, or ``None`` if it does not exist."""

        # TODO (Exercise 02): call `self._container.read_item(...)` and
        # return `None` on failure. Emit `logger.info(...)` with the id and
        # whether the item was found.
        raise NotImplementedError

    def search_products(self, text: str, limit: int = 10) -> list[dict[str, Any]]:
        """Free-text CONTAINS search across product name, brand, and description."""

        # TODO (Exercise 02): SELECT TOP @limit ... WHERE CONTAINS(LOWER(...)).
        # Log via `_log_query(...)`.
        raise NotImplementedError

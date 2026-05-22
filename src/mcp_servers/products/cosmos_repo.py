"""Read-only Cosmos DB repository for the Pepsico products catalog.

You implement this file in **Exercise 02 / Task 02.02**. Every method should
return plain Python ``dict``s so the MCP server can JSON-serialise the result
straight back to the caller.

Reference solution: ``solution/mcp_servers/products/cosmos_repo.py``.
"""

from __future__ import annotations

from typing import Any

from src.common.cosmos import get_container
from src.common.settings import get_settings


class ProductsRepository:
    def __init__(self) -> None:
        settings = get_settings()
        self._container = get_container(settings.cosmos_products_container)

    def list_categories(self) -> list[str]:
        """Return every distinct ``c.category`` value in the products container."""

        # TODO (Exercise 02): run a `SELECT DISTINCT VALUE c.category FROM c`
        # query and return the list.
        raise NotImplementedError

    def list_products(self, category: str | None = None, limit: int = 20) -> list[dict[str, Any]]:
        """Return up to ``limit`` products, optionally filtered by ``category``."""

        # TODO (Exercise 02): SELECT TOP @limit ... with an optional WHERE
        # filter when `category` is provided.
        raise NotImplementedError

    def get_product(self, product_id: str) -> dict[str, Any] | None:
        """Return a single product by id, or ``None`` if it does not exist."""

        # TODO (Exercise 02): call `self._container.read_item(...)` and
        # return `None` on failure.
        raise NotImplementedError

    def search_products(self, text: str, limit: int = 10) -> list[dict[str, Any]]:
        """Free-text CONTAINS search across product name, brand, and description."""

        # TODO (Exercise 02): SELECT TOP @limit ... WHERE CONTAINS(LOWER(...)).
        raise NotImplementedError

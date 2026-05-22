"""Read-only Cosmos DB repository for the Pepsico products catalog."""

from __future__ import annotations

from typing import Any

from src.common.cosmos import get_container
from src.common.settings import get_settings


class ProductsRepository:
    def __init__(self) -> None:
        settings = get_settings()
        self._container = get_container(settings.cosmos_products_container)

    def list_categories(self) -> list[str]:
        query = "SELECT DISTINCT VALUE c.category FROM c"
        return [c for c in self._container.query_items(query=query, enable_cross_partition_query=True)]

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
        return list(
            self._container.query_items(
                query=query, parameters=params, enable_cross_partition_query=True
            )
        )

    def get_product(self, product_id: str) -> dict[str, Any] | None:
        try:
            return self._container.read_item(item=product_id, partition_key=product_id)
        except Exception:
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
        return list(
            self._container.query_items(
                query=query, parameters=params, enable_cross_partition_query=True
            )
        )

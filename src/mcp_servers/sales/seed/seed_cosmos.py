"""Seed the Zava ``sales`` container in Cosmos DB with >1000 generated rows.

Usage:
    zava-seed-sales
    # or
    python -m src.mcp_servers.sales.seed.seed_cosmos

The container is created with ``/id`` as the partition key if it does not exist.
Rows are produced deterministically by :mod:`generate`, so re-running upserts
the same documents (idempotent).
"""

from __future__ import annotations

import logging

from azure.cosmos import PartitionKey
from azure.cosmos.exceptions import CosmosResourceExistsError

from src.common.cosmos import get_cosmos_client
from src.common.settings import get_settings

from .generate import generate_rows

LOG = logging.getLogger(__name__)


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    settings = get_settings()
    client = get_cosmos_client()

    db = client.create_database_if_not_exists(id=settings.cosmos_database)
    LOG.info("Using database '%s'", settings.cosmos_database)

    try:
        container = db.create_container(
            id=settings.cosmos_sales_container,
            partition_key=PartitionKey(path="/id"),
        )
        LOG.info("Created container '%s'", settings.cosmos_sales_container)
    except CosmosResourceExistsError:
        container = db.get_container_client(settings.cosmos_sales_container)
        LOG.info("Container '%s' already exists", settings.cosmos_sales_container)

    documents = generate_rows()
    for document in documents:
        container.upsert_item(body=document)
    LOG.info("Upserted %d sales order lines", len(documents))


if __name__ == "__main__":
    main()

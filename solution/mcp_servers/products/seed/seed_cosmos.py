"""Seed the Pepsico products container in Cosmos DB.

Usage:
    pepsico-seed-products
    # or
    python -m src.mcp_servers.products.seed.seed_cosmos

The container is created with `/id` as the partition key if it does not exist.
"""

from __future__ import annotations

import json
import logging
from pathlib import Path

from azure.cosmos import PartitionKey
from azure.cosmos.exceptions import CosmosResourceExistsError

from src.common.cosmos import get_cosmos_client
from src.common.settings import get_settings

LOG = logging.getLogger(__name__)
SEED_FILE = Path(__file__).with_name("products_seed.json")


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    settings = get_settings()
    client = get_cosmos_client()

    db = client.create_database_if_not_exists(id=settings.cosmos_database)
    LOG.info("Using database '%s'", settings.cosmos_database)

    try:
        container = db.create_container(
            id=settings.cosmos_products_container,
            partition_key=PartitionKey(path="/id"),
        )
        LOG.info("Created container '%s'", settings.cosmos_products_container)
    except CosmosResourceExistsError:
        container = db.get_container_client(settings.cosmos_products_container)
        LOG.info("Container '%s' already exists", settings.cosmos_products_container)

    documents = json.loads(SEED_FILE.read_text(encoding="utf-8"))
    for document in documents:
        container.upsert_item(body=document)
    LOG.info("Upserted %d products", len(documents))


if __name__ == "__main__":
    main()

"""Seed the Pepsico products container in Cosmos DB.

Usage:
    python -m src.mcp_servers.products.seed.seed_cosmos

Prerequisites:
    The database and container must already exist. They are created via the
    Azure control plane (see docs/02_products_mcp_server/02_01_seed_cosmos.md):

        az cosmosdb sql database create \\
            --account-name <account> --resource-group <rg> --name <db>
        az cosmosdb sql container create \\
            --account-name <account> --resource-group <rg> \\
            --database-name <db> --name <container> --partition-key-path /id

    The Cosmos DB Built-in Data Contributor data-plane role does NOT grant
    `sqlDatabases/write`, so this script only performs item upserts.
"""

from __future__ import annotations

import json
import logging
from pathlib import Path

from src.common.cosmos import get_cosmos_client
from src.common.settings import get_settings

LOG = logging.getLogger(__name__)
SEED_FILE = Path(__file__).with_name("products_seed.json")


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    settings = get_settings()
    client = get_cosmos_client()

    db = client.get_database_client(settings.cosmos_database)
    container = db.get_container_client(settings.cosmos_products_container)
    LOG.info(
        "Seeding database '%s' container '%s'",
        settings.cosmos_database,
        settings.cosmos_products_container,
    )

    documents = json.loads(SEED_FILE.read_text(encoding="utf-8"))
    for document in documents:
        container.upsert_item(body=document)
    LOG.info("Upserted %d products", len(documents))


if __name__ == "__main__":
    main()

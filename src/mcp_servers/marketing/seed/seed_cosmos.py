"""Seed the Pepsico marketing_campaigns container in Cosmos DB.

Usage:
    python -m src.mcp_servers.marketing.seed.seed_cosmos

Prerequisites:
    The database and container must already exist. They are created via the
    Azure control plane (see docs/04_marketing_mcp_server/04_01_seed_cosmos.md).
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
SEED_FILE = Path(__file__).with_name("marketing_seed.json")


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    settings = get_settings()
    client = get_cosmos_client()

    db = client.get_database_client(settings.cosmos_database)
    container = db.get_container_client(settings.cosmos_marketing_container)
    LOG.info(
        "Seeding database '%s' container '%s'",
        settings.cosmos_database,
        settings.cosmos_marketing_container,
    )

    documents = json.loads(SEED_FILE.read_text(encoding="utf-8"))
    for document in documents:
        container.upsert_item(body=document)
    LOG.info("Upserted %d campaigns", len(documents))


if __name__ == "__main__":
    main()

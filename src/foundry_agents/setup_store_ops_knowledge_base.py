"""Provision the **Zava store-ops** Foundry IQ knowledge base.

You implement this script in **Exercise 06 / Task 06.01**. The reference
implementation does three things, in order:

1. Uploads the Markdown files under ``src/knowledge_seed/store_ops/`` to an
   Azure AI Search **index** named ``STORE_OPS_KB_SOURCE_ID``. The index
   includes a **filterable ``store_id`` field** parsed from each file's
   YAML frontmatter so retrieval can be scoped to a single Zava store.
2. Wraps the index in a **Foundry IQ knowledge base** named
   ``STORE_OPS_KB_NAME``.
3. Registers a **project connection** named ``STORE_OPS_KB_CONNECTION_NAME``
   so the store-ops Foundry agent (Task 06.02) can call it over MCP via
   the project's managed identity.

Pre-requisites:

* ``AZURE_SEARCH_ENDPOINT``, ``AZURE_AI_PROJECT_RESOURCE_ID``, and the
  ``STORE_OPS_KB_*`` variables filled in ``.env``.
* Your user (or the Foundry project's managed identity) has the
  ``Search Service Contributor`` and ``Search Index Data Contributor``
  roles on the Search service.

Run:

    python -m src.foundry_agents.setup_store_ops_knowledge_base

Reference solution: ``solution/foundry_agents/setup_store_ops_knowledge_base.py``.
"""

from __future__ import annotations

import logging
from pathlib import Path

# TODO (Exercise 06 / Task 06.01): import the helpers you will need.
#   import json, re, time, uuid, requests
#   from azure.identity import get_bearer_token_provider
#   from src.common.foundry_client import get_credential, upsert_project_connection
#   from src.common.settings import get_settings

LOG = logging.getLogger(__name__)

SEARCH_API_VERSION = "2025-11-01-preview"
STORE_OPS_DOCS = Path(__file__).resolve().parents[1] / "knowledge_seed" / "store_ops"


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")

    # TODO (Exercise 06 / Task 06.01):
    #
    # 1. Read settings, ensure AZURE_SEARCH_ENDPOINT is set.
    # 2. Create / update the Search index with fields:
    #      id, title (filterable), content, source (filterable),
    #      store_id (filterable, facetable), doc_type (filterable, facetable).
    # 3. Parse each Markdown file's YAML frontmatter (--- ... ---) and pull
    #    out store_id, doc_type, title. Default store_id to 'all'.
    # 4. Upload every Markdown file under STORE_OPS_DOCS to the index.
    # 5. Create / update the Foundry IQ knowledge base wrapping that index.
    # 6. Register the project connection pointing at
    #       f"{endpoint}/knowledgebases/{kb_name}/mcp?api-version={SEARCH_API_VERSION}"
    #    with category="RemoteTool", audience="https://search.azure.com/".

    raise NotImplementedError(
        "setup_store_ops_knowledge_base is not implemented yet — "
        "complete Exercise 06 / Task 06.01."
    )


if __name__ == "__main__":
    main()

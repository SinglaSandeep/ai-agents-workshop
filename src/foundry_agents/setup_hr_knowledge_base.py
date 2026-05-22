"""Provision the HR Foundry IQ knowledge base and the project connection.

You implement this script in **Exercise 06 / Task 06.01**. The reference
implementation does three things, in order:

1. Uploads the Markdown files under ``src/knowledge_seed/hr/`` to an Azure
   AI Search **index** named ``HR_KB_SOURCE_ID``.
2. Wraps the index in a **Foundry IQ knowledge base** named ``HR_KB_NAME``.
3. Registers a **project connection** named ``HR_KB_CONNECTION_NAME`` so the
   HR Foundry agent (Task 06.02) can call it over MCP via the project's
   managed identity.

It talks to Azure AI Search through the preview REST API to match what the
Foundry IQ portal would create.

Pre-requisites:

* ``AZURE_SEARCH_ENDPOINT``, ``AZURE_AI_PROJECT_RESOURCE_ID``, and the
  ``HR_KB_*`` variables filled in ``.env``.
* Your user (or the Foundry project's managed identity) has the
  ``Search Service Contributor`` and ``Search Index Data Contributor`` roles
  on the Search service.

Run:

    python -m src.foundry_agents.setup_hr_knowledge_base

Reference solution: ``solution/foundry_agents/setup_hr_knowledge_base.py``.
"""

from __future__ import annotations

import logging
from pathlib import Path

# TODO (Exercise 06 / Task 06.01): import the helpers you will need.
#   import json, time, uuid, requests
#   from azure.identity import get_bearer_token_provider
#   from src.common.foundry_client import get_credential, upsert_project_connection
#   from src.common.settings import get_settings

LOG = logging.getLogger(__name__)

SEARCH_API_VERSION = "2025-11-01-preview"
HR_DOCS = Path(__file__).resolve().parents[1] / "knowledge_seed" / "hr"


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")

    # TODO (Exercise 06 / Task 06.01):
    #
    # 1. Read settings, ensure AZURE_SEARCH_ENDPOINT is set.
    # 2. Create / update the Search index with fields: id, title, content, source.
    # 3. Upload every Markdown file under HR_DOCS to the index.
    # 4. Create / update the Foundry IQ knowledge base wrapping that index.
    # 5. Register the project connection pointing at
    #       f"{endpoint}/knowledgebases/{kb_name}/mcp?api-version={SEARCH_API_VERSION}"
    #    with category="RemoteTool", audience="https://search.azure.com/".

    raise NotImplementedError(
        "setup_hr_knowledge_base is not implemented yet — complete Exercise 06 / Task 06.01."
    )


if __name__ == "__main__":
    main()

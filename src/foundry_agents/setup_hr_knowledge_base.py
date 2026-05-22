"""Provision the HR Foundry IQ knowledge base and the Foundry project connection.

This script does three things, in order:

1. Uploads the Markdown files under ``src/knowledge_seed/hr/`` to an Azure AI
   Search **index** named ``HR_KB_SOURCE_ID``.
2. Wraps the index in a **Foundry IQ knowledge base** named ``HR_KB_NAME``
   (a logical surface that an agent can query via MCP).
3. Registers a **project connection** named ``HR_KB_CONNECTION_NAME`` so the
   Foundry agent can reach the knowledge base over MCP via the project's
   managed identity.

It uses the Azure AI Search REST API directly (rather than `azure-search-documents`)
so that all of these resources are created with their preview API versions and
match what the Foundry IQ portal would create.

Pre-requisites:
- `AZURE_SEARCH_ENDPOINT`, `AZURE_AI_PROJECT_RESOURCE_ID`, and `HR_KB_*`
  variables filled in `.env`.
- Your user (or the Foundry project's managed identity) has
  `Search Service Contributor` and `Search Index Data Contributor` on the
  Search service.

Run:
    python -m src.foundry_agents.setup_hr_knowledge_base
"""

from __future__ import annotations

import json
import logging
import time
import uuid
from pathlib import Path

import requests
from azure.identity import get_bearer_token_provider

from src.common.foundry_client import get_credential, upsert_project_connection
from src.common.settings import get_settings

LOG = logging.getLogger(__name__)

SEARCH_API_VERSION = "2025-11-01-preview"
HR_DOCS = Path(__file__).resolve().parents[1] / "knowledge_seed" / "hr"


def _search_headers() -> dict[str, str]:
    cred = get_credential()
    token = get_bearer_token_provider(cred, "https://search.azure.com/.default")()
    return {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}


def _put(url: str, body: dict) -> dict:
    r = requests.put(url, headers=_search_headers(), json=body, timeout=60)
    if not r.ok:
        raise RuntimeError(f"PUT {url} failed: {r.status_code} {r.text}")
    return r.json() if r.text else {}


def _post(url: str, body: dict) -> dict:
    r = requests.post(url, headers=_search_headers(), json=body, timeout=60)
    if not r.ok:
        raise RuntimeError(f"POST {url} failed: {r.status_code} {r.text}")
    return r.json() if r.text else {}


def _create_or_update_index(endpoint: str, index_name: str) -> None:
    body = {
        "name": index_name,
        "fields": [
            {"name": "id", "type": "Edm.String", "key": True, "filterable": True},
            {"name": "title", "type": "Edm.String", "searchable": True, "filterable": True},
            {"name": "content", "type": "Edm.String", "searchable": True},
            {"name": "source", "type": "Edm.String", "filterable": True},
        ],
        "semantic": {
            "configurations": [
                {
                    "name": "default",
                    "prioritizedFields": {
                        "titleField": {"fieldName": "title"},
                        "prioritizedContentFields": [{"fieldName": "content"}],
                    },
                }
            ]
        },
    }
    _put(f"{endpoint}/indexes/{index_name}?api-version={SEARCH_API_VERSION}", body)
    LOG.info("Index '%s' ready", index_name)


def _upload_documents(endpoint: str, index_name: str) -> int:
    docs = []
    for md_file in sorted(HR_DOCS.glob("*.md")):
        docs.append(
            {
                "@search.action": "mergeOrUpload",
                "id": uuid.uuid5(uuid.NAMESPACE_DNS, md_file.name).hex,
                "title": md_file.stem.replace("_", " ").title(),
                "content": md_file.read_text(encoding="utf-8"),
                "source": md_file.name,
            }
        )
    if not docs:
        raise RuntimeError(f"No markdown files found under {HR_DOCS}")
    url = f"{endpoint}/indexes/{index_name}/docs/index?api-version={SEARCH_API_VERSION}"
    _post(url, {"value": docs})
    LOG.info("Uploaded %d HR docs to index '%s'", len(docs), index_name)
    time.sleep(3)  # tiny pause so the docs are searchable before KB creation
    return len(docs)


def _create_or_update_knowledge_base(endpoint: str, kb_name: str, source_index: str) -> None:
    """Create a Foundry IQ knowledge base over the given Search index.

    The Foundry IQ "knowledge base" surface lives at
    ``/knowledgebases/{name}`` on the Search service.
    """
    body = {
        "name": kb_name,
        "description": "Pepsico HR policies, benefits and handbook.",
        "knowledgeSources": [
            {
                "name": source_index,
                "kind": "searchIndex",
                "searchIndexParameters": {"indexName": source_index},
            }
        ],
        "retrievalInstructions": (
            "When answering, prefer information from Pepsico HR policies. "
            "Always cite the source document filename."
        ),
    }
    _put(f"{endpoint}/knowledgebases/{kb_name}?api-version={SEARCH_API_VERSION}", body)
    LOG.info("Knowledge base '%s' ready", kb_name)


def _register_project_connection(search_endpoint: str, kb_name: str, connection_name: str) -> None:
    mcp_target = f"{search_endpoint}/knowledgebases/{kb_name}/mcp?api-version={SEARCH_API_VERSION}"
    upsert_project_connection(
        connection_name=connection_name,
        category="RemoteTool",
        target=mcp_target,
        auth_type="ProjectManagedIdentity",
        audience="https://search.azure.com/",
        metadata={"ApiType": "Azure"},
    )
    LOG.info("Foundry project connection '%s' -> %s", connection_name, mcp_target)


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    settings = get_settings()

    if not settings.azure_search_endpoint:
        raise RuntimeError("AZURE_SEARCH_ENDPOINT is required.")

    endpoint = settings.azure_search_endpoint.rstrip("/")
    index_name = settings.hr_kb_source_id
    kb_name = settings.hr_kb_name

    _create_or_update_index(endpoint, index_name)
    _upload_documents(endpoint, index_name)
    _create_or_update_knowledge_base(endpoint, kb_name, index_name)
    _register_project_connection(endpoint, kb_name, settings.hr_kb_connection_name)

    print(
        json.dumps(
            {
                "search_index": index_name,
                "knowledge_base": kb_name,
                "project_connection": settings.hr_kb_connection_name,
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()

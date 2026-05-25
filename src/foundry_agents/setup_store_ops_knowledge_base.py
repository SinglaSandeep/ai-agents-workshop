"""Provision the **Zava store-ops** Foundry IQ knowledge base.

This script does three things:

1. Uploads the Markdown files under ``src/knowledge_seed/store_ops/`` to an
   Azure AI Search **index** named ``STORE_OPS_KB_SOURCE_ID``. The index
   includes a **filterable ``store_id`` field** parsed from each Markdown
   file's YAML frontmatter — so the store-ops agent (or the orchestrator)
   can scope retrieval to a single Zava store like ``seattle``.
2. Wraps the index in a **Foundry IQ knowledge base** named
   ``STORE_OPS_KB_NAME``.
3. Registers a **project connection** named ``STORE_OPS_KB_CONNECTION_NAME``
   so the Foundry agent can reach the knowledge base over MCP via the
   project's managed identity.

Run:
    python -m src.foundry_agents.setup_store_ops_knowledge_base
"""

from __future__ import annotations

import json
import logging
import re
import time
import uuid
from pathlib import Path

import requests
from azure.identity import get_bearer_token_provider

from src.common.foundry_client import get_credential, upsert_project_connection
from src.common.settings import get_settings

LOG = logging.getLogger(__name__)

SEARCH_API_VERSION = "2025-11-01-preview"
STORE_OPS_DOCS = Path(__file__).resolve().parents[1] / "knowledge_seed" / "store_ops"

_FRONTMATTER_RE = re.compile(r"^---\s*\n(.*?)\n---\s*\n(.*)$", re.DOTALL)


def _parse_frontmatter(text: str) -> tuple[dict[str, str], str]:
    """Parse a minimal YAML-style ``---`` frontmatter block.

    Supports scalar string values like ``store_id: seattle``. Returns
    ``({}, text)`` if no frontmatter is present.
    """
    m = _FRONTMATTER_RE.match(text)
    if not m:
        return {}, text
    block, body = m.group(1), m.group(2)
    fields: dict[str, str] = {}
    for line in block.splitlines():
        if ":" not in line:
            continue
        key, _, value = line.partition(":")
        fields[key.strip()] = value.strip().strip('"').strip("'")
    return fields, body


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
            # Zava-specific filterables — every store-ops Markdown carries
            # a `store_id` frontmatter value (use 'all' for chain-wide policies).
            {"name": "store_id", "type": "Edm.String", "filterable": True, "facetable": True},
            {"name": "doc_type", "type": "Edm.String", "filterable": True, "facetable": True},
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
    for md_file in sorted(STORE_OPS_DOCS.glob("*.md")):
        raw = md_file.read_text(encoding="utf-8")
        fm, body = _parse_frontmatter(raw)
        docs.append(
            {
                "@search.action": "mergeOrUpload",
                "id": uuid.uuid5(uuid.NAMESPACE_DNS, md_file.name).hex,
                "title": fm.get("title", md_file.stem.replace("_", " ").title()),
                "content": body,
                "source": md_file.name,
                "store_id": fm.get("store_id", "all"),
                "doc_type": fm.get("doc_type", "policy"),
            }
        )
    if not docs:
        raise RuntimeError(f"No markdown files found under {STORE_OPS_DOCS}")
    url = f"{endpoint}/indexes/{index_name}/docs/index?api-version={SEARCH_API_VERSION}"
    _post(url, {"value": docs})
    LOG.info("Uploaded %d store-ops docs to index '%s'", len(docs), index_name)
    time.sleep(3)
    return len(docs)


def _create_or_update_knowledge_source(endpoint: str, source_name: str, index_name: str) -> None:
    """Create / update a SearchIndexKnowledgeSource that wraps the index.

    In API version 2025-11-01-preview the knowledge base no longer accepts
    inline ``kind: searchIndex`` entries; each source must be a separate
    ``/knowledgesources/{name}`` resource referenced by name from the KB.
    """
    body = {
        "name": source_name,
        "kind": "searchIndex",
        "description": f"Search index '{index_name}' wrapped as a knowledge source.",
        "searchIndexParameters": {
            "searchIndexName": index_name,
            "sourceDataFields": [
                {"name": "title"},
                {"name": "source"},
                {"name": "store_id"},
                {"name": "doc_type"},
            ],
        },
    }
    _put(f"{endpoint}/knowledgesources/{source_name}?api-version={SEARCH_API_VERSION}", body)
    LOG.info("Knowledge source '%s' ready", source_name)


def _create_or_update_knowledge_base(endpoint: str, kb_name: str, source_name: str) -> None:
    # Note: ``retrievalInstructions`` requires a ``chatCompletionModel`` to be
    # bound to the KB. We rely on the agent's system prompt to express the
    # same guidance (store_id filtering, cite filenames) instead. For the
    # same reason we pin the retrieval reasoning effort to ``minimal`` and
    # request extractive output — anything else also requires a model.
    body = {
        "name": kb_name,
        "description": "Zava store operations: store-manager handbooks, returns, safety, HR, SOPs.",
        "knowledgeSources": [
            {"name": source_name}
        ],
        "outputMode": "extractiveData",
        "retrievalReasoningEffort": {"kind": "minimal"},
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
    index_name = settings.store_ops_kb_source_id
    kb_name = settings.store_ops_kb_name

    _create_or_update_index(endpoint, index_name)
    _upload_documents(endpoint, index_name)
    _create_or_update_knowledge_source(endpoint, index_name, index_name)
    _create_or_update_knowledge_base(endpoint, kb_name, index_name)
    _register_project_connection(endpoint, kb_name, settings.store_ops_kb_connection_name)

    print(
        json.dumps(
            {
                "search_index": index_name,
                "knowledge_base": kb_name,
                "project_connection": settings.store_ops_kb_connection_name,
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()

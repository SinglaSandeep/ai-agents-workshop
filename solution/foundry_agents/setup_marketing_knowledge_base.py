"""Provision the **Zava Marketing** Foundry IQ knowledge base.

Mirrors `setup_store_ops_knowledge_base.py` but for Zava marketing briefs
and post-mortems. Run once after seeding Cosmos (Exercise 04) so the hosted
Marketing agent (Exercise 05) has both structured (MCP) and unstructured
(IQ) sources.

The index includes filterable ``category_id`` and ``store_id`` fields parsed
from each Markdown file's YAML frontmatter so the agent can scope retrieval
to a specific category or store.

Run:
    python -m src.foundry_agents.setup_marketing_knowledge_base
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
MARKETING_DOCS = Path(__file__).resolve().parents[1] / "knowledge_seed" / "marketing"

_FRONTMATTER_RE = re.compile(r"^---\s*\n(.*?)\n---\s*\n(.*)$", re.DOTALL)


def _parse_frontmatter(text: str) -> tuple[dict[str, str], str]:
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


def _create_index(endpoint: str, index_name: str) -> None:
    body = {
        "name": index_name,
        "fields": [
            {"name": "id", "type": "Edm.String", "key": True, "filterable": True},
            {"name": "title", "type": "Edm.String", "searchable": True, "filterable": True},
            {"name": "content", "type": "Edm.String", "searchable": True},
            {"name": "source", "type": "Edm.String", "filterable": True},
            # Zava-specific filterables.
            {"name": "category_id", "type": "Edm.String", "filterable": True, "facetable": True},
            {"name": "store_id", "type": "Edm.String", "filterable": True, "facetable": True},
            {"name": "doc_type", "type": "Edm.String", "filterable": True, "facetable": True},
            {"name": "campaign_id", "type": "Edm.String", "filterable": True},
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
    for md_file in sorted(MARKETING_DOCS.glob("*.md")):
        raw = md_file.read_text(encoding="utf-8")
        fm, body = _parse_frontmatter(raw)
        docs.append(
            {
                "@search.action": "mergeOrUpload",
                "id": uuid.uuid5(uuid.NAMESPACE_DNS, md_file.name).hex,
                "title": fm.get("title", md_file.stem.replace("_", " ").title()),
                "content": body,
                "source": md_file.name,
                "category_id": fm.get("category_id", "all"),
                "store_id": fm.get("store_id", "all"),
                "doc_type": fm.get("doc_type", "brief"),
                "campaign_id": fm.get("campaign_id", ""),
            }
        )
    if not docs:
        raise RuntimeError(f"No markdown files found under {MARKETING_DOCS}")
    url = f"{endpoint}/indexes/{index_name}/docs/index?api-version={SEARCH_API_VERSION}"
    _post(url, {"value": docs})
    LOG.info("Uploaded %d marketing docs to '%s'", len(docs), index_name)
    time.sleep(3)
    return len(docs)


def _create_knowledge_base(endpoint: str, kb_name: str, source_index: str) -> None:
    body = {
        "name": kb_name,
        "description": "Zava marketing briefs, creative one-pagers and post-mortems.",
        "knowledgeSources": [
            {
                "name": source_index,
                "kind": "searchIndex",
                "searchIndexParameters": {"indexName": source_index},
            }
        ],
        "retrievalInstructions": (
            "Use these Zava marketing briefs and post-mortems to ground campaign "
            "narratives. When the user references a specific store_id or category_id, "
            "narrow retrieval accordingly. Always cite the source document filename."
        ),
    }
    _put(f"{endpoint}/knowledgebases/{kb_name}?api-version={SEARCH_API_VERSION}", body)
    LOG.info("Knowledge base '%s' ready", kb_name)


def _register_connection(search_endpoint: str, kb_name: str, connection_name: str) -> None:
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
    index_name = settings.marketing_kb_source_id
    kb_name = settings.marketing_kb_name

    _create_index(endpoint, index_name)
    _upload_documents(endpoint, index_name)
    _create_knowledge_base(endpoint, kb_name, index_name)
    _register_connection(endpoint, kb_name, settings.marketing_kb_connection_name)

    print(
        json.dumps(
            {
                "search_index": index_name,
                "knowledge_base": kb_name,
                "project_connection": settings.marketing_kb_connection_name,
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()

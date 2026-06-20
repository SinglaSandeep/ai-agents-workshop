"""Provision the **Zava Marketing** Foundry IQ knowledge base.

Uses the official ``azure-search-documents`` SDK (preview) with
``AzureKeyCredential`` for AI Search, mirroring the pattern in
https://github.com/Azure-Samples/azure-search-python-samples/blob/main/agentic-retrieval-pipeline-example/agent-example.ipynb

Pipeline:
1. Create / update a Search index for the marketing docs.
2. Upload the markdown files under ``src/knowledge_seed/marketing/``.
3. Create / update a ``SearchIndexKnowledgeSource`` wrapping that index.
4. Create / update a ``KnowledgeBase`` referencing that source.

The Foundry connection that lets the marketing agent reach this KB over MCP
is created **manually** in the portal (account-scoped, key-based) and
referenced by name via ``MARKETING_KB_CONNECTION_NAME``.

Run:
    python -m src.foundry_agents.setup_marketing_knowledge_base
"""

from __future__ import annotations

import json
import logging
import re
import uuid
from pathlib import Path

from azure.core.credentials import AzureKeyCredential
from azure.search.documents import SearchIndexingBufferedSender
from azure.search.documents.indexes import SearchIndexClient
from azure.search.documents.indexes.models import (
    KnowledgeBase,
    KnowledgeRetrievalMinimalReasoningEffort,
    KnowledgeRetrievalOutputMode,
    KnowledgeSourceReference,
    SearchField,
    SearchIndex,
    SearchIndexFieldReference,
    SearchIndexKnowledgeSource,
    SearchIndexKnowledgeSourceParameters,
    SemanticConfiguration,
    SemanticField,
    SemanticPrioritizedFields,
    SemanticSearch,
)

from src.common.foundry_client import get_credential
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


def _search_credential():
    """Prefer AI Search admin key when set; otherwise fall back to AAD."""
    settings = get_settings()
    if settings.azure_search_api_key:
        return AzureKeyCredential(settings.azure_search_api_key)
    return get_credential()


def _create_index(index_client: SearchIndexClient, index_name: str) -> None:
    index = SearchIndex(
        name=index_name,
        fields=[
            SearchField(name="id", type="Edm.String", key=True, filterable=True),
            SearchField(name="title", type="Edm.String", searchable=True, filterable=True),
            SearchField(name="content", type="Edm.String", searchable=True),
            SearchField(name="source", type="Edm.String", filterable=True),
            SearchField(
                name="category_id", type="Edm.String", filterable=True, facetable=True
            ),
            SearchField(
                name="store_id", type="Edm.String", filterable=True, facetable=True
            ),
            SearchField(
                name="doc_type", type="Edm.String", filterable=True, facetable=True
            ),
            SearchField(name="campaign_id", type="Edm.String", filterable=True),
        ],
        semantic_search=SemanticSearch(
            default_configuration_name="default",
            configurations=[
                SemanticConfiguration(
                    name="default",
                    prioritized_fields=SemanticPrioritizedFields(
                        title_field=SemanticField(field_name="title"),
                        content_fields=[SemanticField(field_name="content")],
                    ),
                )
            ],
        ),
    )
    index_client.create_or_update_index(index)
    LOG.info("Index '%s' ready", index_name)


def _upload_documents(endpoint: str, credential, index_name: str) -> int:
    docs = []
    for md_file in sorted(MARKETING_DOCS.glob("*.md")):
        raw = md_file.read_text(encoding="utf-8")
        fm, body = _parse_frontmatter(raw)
        docs.append(
            {
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
    with SearchIndexingBufferedSender(
        endpoint=endpoint, index_name=index_name, credential=credential
    ) as client:
        client.upload_documents(documents=docs)
    LOG.info("Uploaded %d marketing docs to '%s'", len(docs), index_name)
    return len(docs)


def _create_knowledge_source(
    index_client: SearchIndexClient, source_name: str, index_name: str
) -> None:
    ks = SearchIndexKnowledgeSource(
        name=source_name,
        description=f"Search index '{index_name}' wrapped as a knowledge source.",
        search_index_parameters=SearchIndexKnowledgeSourceParameters(
            search_index_name=index_name,
            source_data_fields=[
                SearchIndexFieldReference(name="title"),
                SearchIndexFieldReference(name="source"),
                SearchIndexFieldReference(name="category_id"),
                SearchIndexFieldReference(name="store_id"),
            ],
        ),
    )
    index_client.create_or_update_knowledge_source(knowledge_source=ks)
    LOG.info("Knowledge source '%s' ready", source_name)


def _create_knowledge_base(
    index_client: SearchIndexClient, kb_name: str, source_name: str
) -> None:
    kb = KnowledgeBase(
        name=kb_name,
        description="Zava marketing briefs, creative one-pagers and post-mortems.",
        knowledge_sources=[KnowledgeSourceReference(name=source_name)],
        output_mode=KnowledgeRetrievalOutputMode.EXTRACTIVE_DATA,
        retrieval_reasoning_effort=KnowledgeRetrievalMinimalReasoningEffort(),
    )
    index_client.create_or_update_knowledge_base(knowledge_base=kb)
    LOG.info("Knowledge base '%s' ready", kb_name)


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    settings = get_settings()

    if not settings.azure_search_endpoint:
        raise RuntimeError("AZURE_SEARCH_ENDPOINT is required.")

    endpoint = settings.azure_search_endpoint.rstrip("/")
    index_name = settings.marketing_kb_source_id
    kb_name = settings.marketing_kb_name
    source_name = index_name  # one knowledge source per index

    credential = _search_credential()
    index_client = SearchIndexClient(
        endpoint=endpoint, credential=credential, api_version=SEARCH_API_VERSION
    )

    _create_index(index_client, index_name)
    _upload_documents(endpoint, credential, index_name)
    _create_knowledge_source(index_client, source_name, index_name)
    _create_knowledge_base(index_client, kb_name, source_name)

    print(
        json.dumps(
            {
                "search_index": index_name,
                "knowledge_source": source_name,
                "knowledge_base": kb_name,
                "project_connection": settings.marketing_kb_connection_name,
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()

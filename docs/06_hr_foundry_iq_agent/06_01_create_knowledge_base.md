---
title: '1. Create the HR knowledge base'
layout: default
nav_order: 1
parent: 'Exercise 06: HR Foundry IQ Agent'
---

# Task 06.01 — Create the HR Foundry IQ Knowledge Base

## Introduction

`src/knowledge_seed/hr/` ships a handful of Pepsico HR policy Markdown files.
You will write a one-shot script that:

1. Uploads each `*.md` into an Azure AI Search **index**.
2. Wraps the index in a Foundry IQ **knowledge base**.
3. Registers a Foundry project **connection** that the agent will use to
   call the KB's MCP endpoint.

Everything is done via the preview REST API of Azure AI Search to match what
the Foundry IQ portal would create.

## Success Criteria

* `python -m src.foundry_agents.setup_hr_knowledge_base` runs cleanly and
  prints a JSON summary.
* The Search index `pepsico-hr-source` lists the seed documents.
* The KB endpoint
  `https://<search>.search.windows.net/knowledgebases/pepsico-hr-kb` returns
  HTTP 200 to a GET (via the portal).
* Foundry project connection `pepsico-hr-kb-conn` exists.

## Key Tasks

### 01: Inspect the seed docs

List `src/knowledge_seed/hr/`. Each file is a short Markdown policy:

```
pepsico_benefits_summary.md
pepsico_pto_policy.md
...
```

### 02: Implement `setup_hr_knowledge_base.py`

Open [src/foundry_agents/setup_hr_knowledge_base.py](https://github.com/SinglaSandeep/ai-agents-workshop/blob/main/src/foundry_agents/setup_hr_knowledge_base.py)
and follow the TODOs.

<details markdown="block">
<summary><strong>Expand this section to view the solution</strong></summary>

```python
"""Provision the HR Foundry IQ knowledge base and the project connection."""

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
            "configurations": [{
                "name": "default",
                "prioritizedFields": {
                    "titleField": {"fieldName": "title"},
                    "prioritizedContentFields": [{"fieldName": "content"}],
                },
            }]
        },
    }
    _put(f"{endpoint}/indexes/{index_name}?api-version={SEARCH_API_VERSION}", body)
    LOG.info("Index '%s' ready", index_name)


def _upload_documents(endpoint: str, index_name: str) -> int:
    docs = []
    for md_file in sorted(HR_DOCS.glob("*.md")):
        docs.append({
            "@search.action": "mergeOrUpload",
            "id": uuid.uuid5(uuid.NAMESPACE_DNS, md_file.name).hex,
            "title": md_file.stem.replace("_", " ").title(),
            "content": md_file.read_text(encoding="utf-8"),
            "source": md_file.name,
        })
    if not docs:
        raise RuntimeError(f"No markdown files found under {HR_DOCS}")
    url = f"{endpoint}/indexes/{index_name}/docs/index?api-version={SEARCH_API_VERSION}"
    _post(url, {"value": docs})
    LOG.info("Uploaded %d HR docs", len(docs))
    time.sleep(3)
    return len(docs)


def _create_or_update_kb(endpoint: str, kb_name: str, source_index: str) -> None:
    body = {
        "name": kb_name,
        "description": "Pepsico HR policies, benefits and handbook.",
        "knowledgeSources": [{
            "name": source_index,
            "kind": "searchIndex",
            "searchIndexParameters": {"indexName": source_index},
        }],
        "retrievalInstructions": (
            "When answering, prefer information from Pepsico HR policies. "
            "Always cite the source document filename."
        ),
    }
    _put(f"{endpoint}/knowledgebases/{kb_name}?api-version={SEARCH_API_VERSION}", body)
    LOG.info("Knowledge base '%s' ready", kb_name)


def _register_connection(endpoint: str, kb_name: str, connection_name: str) -> None:
    target = f"{endpoint}/knowledgebases/{kb_name}/mcp?api-version={SEARCH_API_VERSION}"
    upsert_project_connection(
        connection_name=connection_name,
        category="RemoteTool",
        target=target,
        auth_type="ProjectManagedIdentity",
        audience="https://search.azure.com/",
        metadata={"ApiType": "Azure"},
    )
    LOG.info("Project connection '%s' -> %s", connection_name, target)


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
    _create_or_update_kb(endpoint, kb_name, index_name)
    _register_connection(endpoint, kb_name, settings.hr_kb_connection_name)

    print(json.dumps({
        "search_index": index_name,
        "knowledge_base": kb_name,
        "project_connection": settings.hr_kb_connection_name,
    }, indent=2))


if __name__ == "__main__":
    main()
```

</details>

### 03: Run it

```powershell
python -m src.foundry_agents.setup_hr_knowledge_base
```

## Next

Continue to [06.02 — Create the HR Prompt Agent](06_02_create_hr_agent.md).

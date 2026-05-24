---
title: '2. Build the hosted Marketing agent'
layout: default
nav_order: 2
parent: 'Exercise 05: Marketing Hosted Agent (Foundry IQ + Web Tool)'
---

# Task 05.02 — Build the Hosted Marketing Agent

## Introduction

Foundry hosted agents follow a simple contract: your code creates an
`agent_framework.Agent`, hands it to
`agent_framework_foundry_hosting.ResponsesHostServer`, and calls `.run()`. The
hosted runtime exposes that agent over the **OpenAI Responses API** on port
`8088` and takes care of identity, tracing, content-safety, and scaling.

The agent code lives under [src/foundry_agents/marketing_hosted/](https://github.com/SinglaSandeep/ai-agents-workshop/blob/main/src/foundry_agents/marketing_hosted/)
and ships as its own Docker image:

```text
src/foundry_agents/marketing_hosted/
├── agent.yaml        # azd ai agent manifest (kind: hosted)
├── Dockerfile
├── main.py           # ResponsesHostServer entrypoint
├── pyproject.toml    # only the agent deps (decoupled from chat app)
└── README.md
```

## Success Criteria

* `marketing_hosted/main.py` builds an `Agent` with three MCP tools attached:
  Marketing MCP, Foundry Toolbox (web search + code interpreter), Marketing IQ KB.
* `agent.yaml` declares `kind: hosted`, the `responses` protocol, and the
  environment variables the agent expects.

## Key Tasks

### 01: Implement `main()`

Open [src/foundry_agents/marketing_hosted/main.py](https://github.com/SinglaSandeep/ai-agents-workshop/blob/main/src/foundry_agents/marketing_hosted/main.py).

<details markdown="block">
<summary><strong>Expand to view the solution</strong></summary>

```python
"""Foundry-hosted Marketing agent (Microsoft Agent Framework)."""
from __future__ import annotations

import logging
import os

import httpx
import mcp.types
from agent_framework import Agent, MCPStreamableHTTPTool
from agent_framework.foundry import FoundryChatClient
from agent_framework.observability import enable_instrumentation
from agent_framework_foundry_hosting import ResponsesHostServer
from azure.identity import (
    AzureDeveloperCliCredential,
    ChainedTokenCredential,
    ManagedIdentityCredential,
    get_bearer_token_provider,
)

logger = logging.getLogger("marketing-hosted-agent")

PROJECT_ENDPOINT = os.environ["FOUNDRY_PROJECT_ENDPOINT"]
MODEL_DEPLOYMENT = os.environ["AZURE_AI_MODEL_DEPLOYMENT_NAME"]
TOOLBOX_NAME = os.environ.get("CUSTOM_FOUNDRY_AGENT_TOOLBOX_NAME", "pepsico-marketing-tools")
SEARCH_ENDPOINT = os.environ["AZURE_AI_SEARCH_SERVICE_ENDPOINT"]
KB_NAME = os.environ.get("AZURE_AI_SEARCH_KNOWLEDGE_BASE_NAME", "pepsico-marketing-kb")
MARKETING_MCP_URL = os.environ["MARKETING_MCP_URL"]

INSTRUCTIONS = """You are the Pepsico Marketing Specialist running inside Microsoft Foundry.

You have THREE tools:

1. The `marketing_mcp` MCP server: authoritative campaign records (status,
   budget, channels, KPIs) backed by Cosmos DB. Use this for any structured
   campaign data lookup.
2. The Foundry Toolbox MCP (`toolbox`) which exposes `web_search` and
   `code_interpreter`. Use `web_search` ONLY for live news / competitor /
   industry context that is too recent for the model's training data.
3. The `marketing_kb` MCP server (Foundry IQ) which exposes
   `knowledge_base_retrieve` over indexed Pepsico marketing briefs.

Rules:
- Never make up Pepsico campaign data. Prefer `marketing_mcp` for structured
  facts, `marketing_kb` for narrative briefs.
- When you cite the web, always include the URL.
- End every answer with: `Tools used: ...`.
"""


class BearerAuth(httpx.Auth):
    def __init__(self, token_provider):
        self._token_provider = token_provider

    def auth_flow(self, request):
        request.headers["Authorization"] = f"Bearer {self._token_provider()}"
        yield request


# Workaround for Azure AI Search KB MCP returning empty uri values.
for _cls in [mcp.types.ResourceContents, mcp.types.TextResourceContents, mcp.types.BlobResourceContents]:
    _cls.model_fields["uri"].annotation = str | None
    _cls.model_fields["uri"].default = None
    _cls.model_fields["uri"].metadata = []
for _cls in [mcp.types.ResourceContents, mcp.types.TextResourceContents,
             mcp.types.BlobResourceContents, mcp.types.EmbeddedResource,
             mcp.types.CallToolResult]:
    _cls.model_rebuild(force=True)


def main() -> None:
    credential = ChainedTokenCredential(
        ManagedIdentityCredential(client_id=os.getenv("AZURE_CLIENT_ID")),
        AzureDeveloperCliCredential(tenant_id=os.getenv("AZURE_TENANT_ID"), process_timeout=60),
    )

    # 1) Marketing MCP server (Cosmos truth).
    marketing_mcp = MCPStreamableHTTPTool(
        name="marketing_mcp",
        url=MARKETING_MCP_URL,
        load_prompts=False,
    )

    # 2) Foundry Toolbox MCP (web_search + code_interpreter).
    toolbox_url = f"{PROJECT_ENDPOINT.rstrip('/')}/toolboxes/{TOOLBOX_NAME}/mcp?api-version=v1"
    ai_token = get_bearer_token_provider(credential, "https://ai.azure.com/.default")
    toolbox = MCPStreamableHTTPTool(
        name="toolbox",
        url=toolbox_url,
        http_client=httpx.AsyncClient(
            auth=BearerAuth(ai_token),
            headers={"Foundry-Features": "Toolboxes=V1Preview"},
            timeout=120.0,
        ),
        allowed_tools=["web_search", "code_interpreter"],
        load_prompts=False,
    )

    # 3) Foundry IQ KB MCP (Marketing briefs).
    kb_url = f"{SEARCH_ENDPOINT.rstrip('/')}/knowledgebases/{KB_NAME}/mcp?api-version=2025-11-01-Preview"
    search_token = get_bearer_token_provider(credential, "https://search.azure.com/.default")
    kb = MCPStreamableHTTPTool(
        name="marketing_kb",
        url=kb_url,
        http_client=httpx.AsyncClient(auth=BearerAuth(search_token), timeout=120.0),
        allowed_tools=["knowledge_base_retrieve"],
        load_prompts=False,
    )

    chat = FoundryChatClient(
        project_endpoint=PROJECT_ENDPOINT,
        model=MODEL_DEPLOYMENT,
        credential=credential,
    )

    agent = Agent(
        client=chat,
        name="PepsicoMarketingSpecialist",
        instructions=INSTRUCTIONS,
        tools=[marketing_mcp, toolbox, kb],
        default_options={"store": False},
    )

    ResponsesHostServer(agent).run()


if __name__ == "__main__":
    logger.setLevel(logging.INFO)
    enable_instrumentation(enable_sensitive_data=False)
    main()
```

</details>

### 02: Review `agent.yaml`

[src/foundry_agents/marketing_hosted/agent.yaml](https://github.com/SinglaSandeep/ai-agents-workshop/blob/main/src/foundry_agents/marketing_hosted/agent.yaml)

```yaml
kind: hosted
name: pepsico-marketing-agent
protocols:
  - protocol: responses
    version: 1.0.0
resources:
  cpu: '0.5'
  memory: '1Gi'
environment_variables:
  - name: AZURE_AI_MODEL_DEPLOYMENT_NAME
    value: ${AZURE_AI_MODEL_DEPLOYMENT_NAME}
  - name: AZURE_AI_SEARCH_SERVICE_ENDPOINT
    value: ${AZURE_AI_SEARCH_SERVICE_ENDPOINT}
  - name: AZURE_AI_SEARCH_KNOWLEDGE_BASE_NAME
    value: pepsico-marketing-kb
  - name: CUSTOM_FOUNDRY_AGENT_TOOLBOX_NAME
    value: pepsico-marketing-tools
  - name: MARKETING_MCP_URL
    value: ${MARKETING_MCP_URL}
```

> **Reserved prefixes.** `FOUNDRY_*` and `AGENT_*` are reserved by the platform.
> `FOUNDRY_PROJECT_ENDPOINT` and `APPLICATIONINSIGHTS_CONNECTION_STRING` are
> injected automatically.

### 03: Create the Foundry Toolbox

In the Foundry portal → **Toolboxes → + New** → name it
`pepsico-marketing-tools` → add the **Web Search** and **Code Interpreter**
built-in tools → **Save**.

(This is the toolbox the agent reaches over MCP at runtime.)

## Next

Continue to [05.03 — Run locally, deploy to Foundry, wire into chat](05_03_deploy_and_wire.md).

"""Foundry-hosted Marketing agent — full reference implementation.

Built on:
- Microsoft Agent Framework (`agent_framework`)
- `agent_framework_foundry_hosting.ResponsesHostServer`
- Foundry Toolbox MCP (web_search + code_interpreter)
- Foundry IQ KB MCP (knowledge_base_retrieve)
- Marketing MCP container app from Exercise 04
"""
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
from dotenv import load_dotenv

from .middleware import content_filter_middleware

load_dotenv(override=True)
logger = logging.getLogger("marketing-hosted-agent")

PROJECT_ENDPOINT = os.environ["FOUNDRY_PROJECT_ENDPOINT"]
MODEL_DEPLOYMENT = os.environ["AZURE_AI_MODEL_DEPLOYMENT_NAME"]
TOOLBOX_NAME = os.environ.get(
    "CUSTOM_FOUNDRY_AGENT_TOOLBOX_NAME", "pepsico-marketing-tools"
)
SEARCH_ENDPOINT = os.environ["AZURE_AI_SEARCH_SERVICE_ENDPOINT"]
KB_NAME = os.environ.get(
    "AZURE_AI_SEARCH_KNOWLEDGE_BASE_NAME", "pepsico-marketing-kb"
)
MARKETING_MCP_URL = os.environ["MARKETING_MCP_URL"]

INSTRUCTIONS = """You are the Pepsico Marketing Specialist running inside Microsoft Foundry.

You have THREE tools:

1. `marketing_mcp` — authoritative campaign records (status, budget, channels,
   KPIs) backed by Cosmos DB.
2. `toolbox` — Foundry Toolbox exposing `web_search` and `code_interpreter`.
   Use `web_search` ONLY for live news / competitor / industry context that is
   too recent for the model's training data.
3. `marketing_kb` — Foundry IQ knowledge base (`knowledge_base_retrieve`) over
   indexed Pepsico marketing briefs.

Rules:
- Never make up Pepsico campaign data.
- When you cite the web, always include the URL.
- End every answer with a line: `Tools used: ...`.
"""


class BearerAuth(httpx.Auth):
    def __init__(self, token_provider):
        self._token_provider = token_provider

    def auth_flow(self, request):
        request.headers["Authorization"] = f"Bearer {self._token_provider()}"
        yield request


# Workaround: Azure AI Search KB MCP can return resource content with empty
# uri values; relax the schema so pydantic validation succeeds.
for _cls in [
    mcp.types.ResourceContents,
    mcp.types.TextResourceContents,
    mcp.types.BlobResourceContents,
]:
    _cls.model_fields["uri"].annotation = str | None
    _cls.model_fields["uri"].default = None
    _cls.model_fields["uri"].metadata = []
for _cls in [
    mcp.types.ResourceContents,
    mcp.types.TextResourceContents,
    mcp.types.BlobResourceContents,
    mcp.types.EmbeddedResource,
    mcp.types.CallToolResult,
]:
    _cls.model_rebuild(force=True)


def main() -> None:
    credential = ChainedTokenCredential(
        ManagedIdentityCredential(client_id=os.getenv("AZURE_CLIENT_ID")),
        AzureDeveloperCliCredential(
            tenant_id=os.getenv("AZURE_TENANT_ID"), process_timeout=60
        ),
    )

    marketing_mcp = MCPStreamableHTTPTool(
        name="marketing_mcp",
        url=MARKETING_MCP_URL,
        load_prompts=False,
    )

    toolbox_url = (
        f"{PROJECT_ENDPOINT.rstrip('/')}/toolboxes/{TOOLBOX_NAME}/mcp?api-version=v1"
    )
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

    kb_url = (
        f"{SEARCH_ENDPOINT.rstrip('/')}/knowledgebases/{KB_NAME}"
        "/mcp?api-version=2025-11-01-Preview"
    )
    search_token = get_bearer_token_provider(
        credential, "https://search.azure.com/.default"
    )
    kb = MCPStreamableHTTPTool(
        name="marketing_kb",
        url=kb_url,
        http_client=httpx.AsyncClient(
            auth=BearerAuth(search_token), timeout=120.0
        ),
        allowed_tools=["knowledge_base_retrieve"],
        load_prompts=False,
    )

    chat = FoundryChatClient(
        project_endpoint=PROJECT_ENDPOINT,
        model=MODEL_DEPLOYMENT,
        credential=credential,
        middleware=[content_filter_middleware],
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

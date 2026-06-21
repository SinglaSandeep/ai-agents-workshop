"""Shared helpers around the Foundry `AIProjectClient` and ARM connections."""

from __future__ import annotations

import logging
from typing import Any

import requests
from azure.ai.projects import AIProjectClient
from azure.identity import DefaultAzureCredential, get_bearer_token_provider

from .settings import get_settings

LOG = logging.getLogger(__name__)


def get_credential() -> DefaultAzureCredential:
    """Return a `DefaultAzureCredential` shared across the workshop."""
    return DefaultAzureCredential(exclude_interactive_browser_credential=False)


def get_project_client() -> AIProjectClient:
    """Build an `AIProjectClient` pointed at the configured Foundry project."""
    settings = get_settings()
    if not settings.azure_ai_project_endpoint:
        raise RuntimeError(
            "AZURE_AI_PROJECT_ENDPOINT is not set. See docs/00_setup/00_03_verify_resources.md"
        )
    return AIProjectClient(endpoint=settings.azure_ai_project_endpoint, credential=get_credential())


def upsert_project_connection(
    connection_name: str,
    *,
    category: str,
    target: str,
    auth_type: str = "ProjectManagedIdentity",
    audience: str | None = None,
    metadata: dict[str, str] | None = None,
    is_shared_to_all: bool = True,
    credentials: dict[str, Any] | None = None,
) -> dict:
    """Create or update a Foundry **project connection** via the ARM REST API.

    Used for: Foundry IQ knowledge-base MCP endpoint (Ex. 03), Products MCP
    endpoint (Ex. 04), Marketing MCP endpoint (Ex. 05).
    """
    settings = get_settings()
    if not settings.azure_ai_project_resource_id:
        raise RuntimeError(
            "AZURE_AI_PROJECT_RESOURCE_ID is required to create project connections."
        )

    credential = get_credential()
    token_provider = get_bearer_token_provider(credential, "https://management.azure.com/.default")
    headers = {
        "Authorization": f"Bearer {token_provider()}",
        "Content-Type": "application/json",
    }

    url = (
        f"https://management.azure.com{settings.azure_ai_project_resource_id}"
        f"/connections/{connection_name}?api-version=2025-10-01-preview"
    )

    properties: dict[str, Any] = {
        "authType": auth_type,
        "category": category,
        "target": target,
        "isSharedToAll": is_shared_to_all,
    }
    if audience:
        properties["audience"] = audience
    if metadata:
        properties["metadata"] = metadata
    if credentials:
        properties["credentials"] = credentials

    body = {
        "name": connection_name,
        "type": "Microsoft.MachineLearningServices/workspaces/connections",
        "properties": properties,
    }

    LOG.info("Upserting Foundry project connection %s", connection_name)
    response = requests.put(url, headers=headers, json=body, timeout=30)
    if not response.ok:
        raise RuntimeError(
            f"Failed to upsert connection {connection_name}: {response.status_code} {response.text}"
        )
    return response.json()


def upsert_mcp_connection(connection_name: str, target: str) -> dict:
    """Create/update a **project-level** MCP connection for an agent's MCP tool.

    The Container Apps MCP servers are protected with HTTP Basic auth, so this
    builds a **Key-based** connection carrying the `Authorization: Basic ...`
    header from `MCP_BASIC_AUTH_USERNAME` / `MCP_BASIC_AUTH_PASSWORD`. Creating
    the connection first (and referencing it via `project_connection_id`) is
    what makes the MCP tool visible at the project level.

    Falls back to an anonymous connection when no credentials are configured.
    """
    settings = get_settings()
    header = settings.mcp_basic_auth_header
    if header:
        return upsert_project_connection(
            connection_name,
            category="RemoteTool",
            target=target,
            auth_type="CustomKeys",
            metadata={"ApiType": "MCP"},
            credentials={"keys": {"Authorization": header}},
        )
    LOG.warning(
        "MCP_BASIC_AUTH_USERNAME/PASSWORD not set — creating anonymous "
        "connection %s. Set them in .env if the server requires auth.",
        connection_name,
    )
    return upsert_project_connection(
        connection_name,
        category="RemoteTool",
        target=target,
        auth_type="None",
        metadata={"ApiType": "MCP"},
    )


def upsert_kb_mcp_connection(connection_name: str, target: str, kb_name: str) -> dict:
    """Create/update the connection that fronts a Foundry IQ **KB MCP** endpoint.

    The knowledge-base MCP endpoint lives on the Azure AI Search service, which
    authenticates with the `api-key` header. This builds a key-based
    `RemoteTool` connection carrying that header from `AZURE_SEARCH_API_KEY`,
    so the marketing agent's KB MCP tool stops returning 401.
    """
    settings = get_settings()
    if not settings.azure_search_api_key:
        raise RuntimeError(
            "AZURE_SEARCH_API_KEY is empty. The KB MCP endpoint needs the AI "
            "Search admin key to authenticate."
        )
    return upsert_project_connection(
        connection_name,
        category="RemoteTool",
        target=target,
        auth_type="CustomKeys",
        metadata={"knowledgeBaseName": kb_name, "type": "knowledgeBase_MCP"},
        credentials={"keys": {"api-key": settings.azure_search_api_key}},
    )


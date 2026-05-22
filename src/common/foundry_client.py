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

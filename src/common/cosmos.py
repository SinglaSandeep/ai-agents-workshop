"""Shared Cosmos DB client builder (passwordless via DefaultAzureCredential)."""

from __future__ import annotations

from azure.cosmos import CosmosClient
from azure.identity import DefaultAzureCredential

from .settings import get_settings

_credential: DefaultAzureCredential | None = None


def _get_credential() -> DefaultAzureCredential:
    # Local helper so the MCP server containers do not need the
    # full Foundry SDK (azure-ai-projects) just to talk to Cosmos.
    global _credential
    if _credential is None:
        _credential = DefaultAzureCredential(exclude_interactive_browser_credential=False)
    return _credential


def get_cosmos_client() -> CosmosClient:
    settings = get_settings()
    if not settings.cosmos_endpoint:
        raise RuntimeError("COSMOS_ENDPOINT is not set. See docs/00_setup/00_03_verify_resources.md")
    return CosmosClient(url=settings.cosmos_endpoint, credential=_get_credential())


def get_container(container_name: str):
    settings = get_settings()
    client = get_cosmos_client()
    database = client.get_database_client(settings.cosmos_database)
    return database.get_container_client(container_name)

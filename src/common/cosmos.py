"""Shared Cosmos DB client builder (passwordless via DefaultAzureCredential)."""

from __future__ import annotations

from azure.cosmos import CosmosClient

from .foundry_client import get_credential
from .settings import get_settings


def get_cosmos_client() -> CosmosClient:
    settings = get_settings()
    if not settings.cosmos_endpoint:
        raise RuntimeError("COSMOS_ENDPOINT is not set. See docs/00_setup/00_03_verify_resources.md")
    return CosmosClient(url=settings.cosmos_endpoint, credential=get_credential())


def get_container(container_name: str):
    settings = get_settings()
    client = get_cosmos_client()
    database = client.get_database_client(settings.cosmos_database)
    return database.get_container_client(container_name)

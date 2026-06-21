"""Centralised, typed settings loaded from `.env`.

Every module in the workshop reads its configuration from here so the
environment surface is documented in exactly one place.
"""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


_REPO_ROOT = Path(__file__).resolve().parents[2]
_ENV_FILE = _REPO_ROOT / ".env"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=_ENV_FILE,
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False,
    )

    # ---- Azure subscription ------------------------------------------------
    azure_subscription_id: str = Field(default="", alias="AZURE_SUBSCRIPTION_ID")
    azure_tenant_id: str = Field(default="", alias="AZURE_TENANT_ID")
    azure_resource_group: str = Field(default="", alias="AZURE_RESOURCE_GROUP")
    # Client ID of a **user-assigned managed identity** to run hosted agents as.
    # When set, the hosted container authenticates as this identity (which must
    # already hold the needed roles); empty = use the system-assigned identity.
    azure_client_id: str = Field(default="", alias="AZURE_CLIENT_ID")
    # User-assigned managed identity for hosted-agent workloads. The resource ID
    # is used by the deploy script to attach the identity to the Foundry account
    # and grant it AcrPull; the client ID is what the container authenticates as
    # at runtime (injected as AZURE_CLIENT_ID). These take precedence over
    # AZURE_CLIENT_ID when set.
    app_identity_resource_id: str = Field(default="", alias="APP_IDENTITY_RESOURCE_ID")
    app_identity_client_id: str = Field(default="", alias="APP_IDENTITY_CLIENT_ID")

    # ---- Foundry project ---------------------------------------------------
    azure_ai_project_endpoint: str = Field(default="", alias="AZURE_AI_PROJECT_ENDPOINT")
    azure_ai_project_name: str = Field(default="", alias="AZURE_AI_PROJECT_NAME")
    azure_ai_model_deployment: str = Field(default="gpt-4.1-mini", alias="AZURE_AI_MODEL_DEPLOYMENT")
    azure_ai_project_resource_id: str = Field(default="", alias="AZURE_AI_PROJECT_RESOURCE_ID")

    # ---- Foundry IQ / Azure AI Search --------------------------------------
    azure_search_endpoint: str = Field(default="", alias="AZURE_SEARCH_ENDPOINT")
    # Optional admin API key. When set, setup scripts use key-based auth
    # instead of AAD bearer tokens (useful when the Search service is
    # configured with `authOptions: apiKeyOnly`).
    azure_search_api_key: str = Field(default="", alias="AZURE_SEARCH_API_KEY")
    marketing_kb_name: str = Field(default="zava-marketing-kb", alias="MARKETING_KB_NAME")
    marketing_kb_source_id: str = Field(
        default="zava-marketing-source", alias="MARKETING_KB_SOURCE_ID"
    )
    marketing_kb_connection_name: str = Field(
        default="srchwrk01", alias="MARKETING_KB_CONNECTION_NAME"
    )
    marketing_toolbox_name: str = Field(
        default="zava-marketing-tools", alias="MARKETING_TOOLBOX_NAME"
    )

    # ---- Cosmos DB ---------------------------------------------------------
    cosmos_endpoint: str = Field(default="", alias="COSMOS_ENDPOINT")
    # Account key for key-based (passwordful) auth. When set, the Cosmos client
    # uses it instead of DefaultAzureCredential. Container Apps inject it as a
    # secret; for local dev leave it blank to use az-login / managed identity.
    cosmos_key: str = Field(default="", alias="COSMOS_KEY")
    cosmos_database: str = Field(default="zava", alias="COSMOS_DATABASE")
    cosmos_sales_container: str = Field(default="sales", alias="COSMOS_SALES_CONTAINER")
    cosmos_inventory_container: str = Field(
        default="inventory", alias="COSMOS_INVENTORY_CONTAINER"
    )
    cosmos_marketing_container: str = Field(
        default="marketing_campaigns", alias="COSMOS_MARKETING_CONTAINER"
    )

    # ---- MCP servers -------------------------------------------------------
    sales_mcp_url: str = Field(default="", alias="SALES_MCP_URL")
    sales_mcp_connection_name: str = Field(
        default="zava-sales-mcp-conn", alias="SALES_MCP_CONNECTION_NAME"
    )
    inventory_mcp_url: str = Field(default="", alias="INVENTORY_MCP_URL")
    inventory_mcp_connection_name: str = Field(
        default="zava-inventory-mcp-conn", alias="INVENTORY_MCP_CONNECTION_NAME"
    )
    marketing_mcp_url: str = Field(default="", alias="MARKETING_MCP_URL")
    marketing_mcp_connection_name: str = Field(
        default="zava-marketing-mcp-conn", alias="MARKETING_MCP_CONNECTION_NAME"
    )

    # ---- Foundry agent names ----------------------------------------------
    sales_agent_name: str = Field(default="zava-sales-agent", alias="SALES_AGENT_NAME")
    inventory_agent_name: str = Field(
        default="zava-inventory-agent", alias="INVENTORY_AGENT_NAME"
    )
    inventory_hosted_agent_name: str = Field(
        default="zava-inventory-hosted-agent", alias="INVENTORY_HOSTED_AGENT_NAME"
    )
    marketing_agent_name: str = Field(default="zava-marketing-agent", alias="MARKETING_AGENT_NAME")
    action_agent_name: str = Field(default="zava-action-agent", alias="ACTION_AGENT_NAME")
    response_agent_name: str = Field(default="zava-response-generator", alias="RESPONSE_AGENT_NAME")
    intent_agent_name: str = Field(default="zava-intent-detector", alias="INTENT_AGENT_NAME")

    # ---- Container Apps ----------------------------------------------------
    aca_environment: str = Field(default="zava-aca-env", alias="ACA_ENVIRONMENT")
    aca_location: str = Field(default="eastus2", alias="ACA_LOCATION")
    acr_name: str = Field(default="", alias="ACR_NAME")

    # ---- Observability -----------------------------------------------------
    applicationinsights_connection_string: str = Field(
        default="", alias="APPLICATIONINSIGHTS_CONNECTION_STRING"
    )
    otel_service_name: str = Field(default="zava-agents-workshop", alias="OTEL_SERVICE_NAME")


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()

"""Centralised, typed settings loaded from `.env`.

Every module in the workshop reads its configuration from here so the
environment surface is documented in exactly one place.
"""

from __future__ import annotations

from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False,
    )

    # ---- Azure subscription ------------------------------------------------
    azure_subscription_id: str = Field(default="", alias="AZURE_SUBSCRIPTION_ID")
    azure_tenant_id: str = Field(default="", alias="AZURE_TENANT_ID")
    azure_resource_group: str = Field(default="", alias="AZURE_RESOURCE_GROUP")

    # ---- Foundry project ---------------------------------------------------
    azure_ai_project_endpoint: str = Field(default="", alias="AZURE_AI_PROJECT_ENDPOINT")
    azure_ai_project_name: str = Field(default="", alias="AZURE_AI_PROJECT_NAME")
    azure_ai_model_deployment: str = Field(default="gpt-4.1-mini", alias="AZURE_AI_MODEL_DEPLOYMENT")
    azure_ai_project_resource_id: str = Field(default="", alias="AZURE_AI_PROJECT_RESOURCE_ID")

    # ---- Foundry IQ / Azure AI Search --------------------------------------
    azure_search_endpoint: str = Field(default="", alias="AZURE_SEARCH_ENDPOINT")
    # Store-ops KB (replaces the former HR KB). Index includes a filterable
    # `store_id` field so the store-ops agent can scope retrieval to a
    # single Zava store.
    store_ops_kb_name: str = Field(default="zava-store-ops-kb", alias="STORE_OPS_KB_NAME")
    store_ops_kb_source_id: str = Field(
        default="zava-store-ops-source", alias="STORE_OPS_KB_SOURCE_ID"
    )
    store_ops_kb_connection_name: str = Field(
        default="zava-store-ops-kb-conn", alias="STORE_OPS_KB_CONNECTION_NAME"
    )
    marketing_kb_name: str = Field(default="zava-marketing-kb", alias="MARKETING_KB_NAME")
    marketing_kb_source_id: str = Field(
        default="zava-marketing-source", alias="MARKETING_KB_SOURCE_ID"
    )
    marketing_kb_connection_name: str = Field(
        default="zava-marketing-kb-conn", alias="MARKETING_KB_CONNECTION_NAME"
    )
    marketing_toolbox_name: str = Field(
        default="zava-marketing-tools", alias="MARKETING_TOOLBOX_NAME"
    )

    # ---- Cosmos DB ---------------------------------------------------------
    cosmos_endpoint: str = Field(default="", alias="COSMOS_ENDPOINT")
    cosmos_database: str = Field(default="zava", alias="COSMOS_DATABASE")
    cosmos_products_container: str = Field(default="products", alias="COSMOS_PRODUCTS_CONTAINER")
    cosmos_marketing_container: str = Field(
        default="marketing_campaigns", alias="COSMOS_MARKETING_CONTAINER"
    )

    # ---- MCP servers -------------------------------------------------------
    products_mcp_url: str = Field(default="", alias="PRODUCTS_MCP_URL")
    products_mcp_connection_name: str = Field(
        default="zava-products-mcp-conn", alias="PRODUCTS_MCP_CONNECTION_NAME"
    )
    marketing_mcp_url: str = Field(default="", alias="MARKETING_MCP_URL")
    marketing_mcp_connection_name: str = Field(
        default="zava-marketing-mcp-conn", alias="MARKETING_MCP_CONNECTION_NAME"
    )

    # ---- Bing Grounding ----------------------------------------------------
    bing_grounding_connection_name: str = Field(
        default="zava-bing-grounding", alias="BING_GROUNDING_CONNECTION_NAME"
    )

    # ---- Foundry agent names ----------------------------------------------
    store_ops_agent_name: str = Field(
        default="zava-store-ops-agent", alias="STORE_OPS_AGENT_NAME"
    )
    products_agent_name: str = Field(default="zava-products-agent", alias="PRODUCTS_AGENT_NAME")
    marketing_agent_name: str = Field(default="zava-marketing-agent", alias="MARKETING_AGENT_NAME")
    response_agent_name: str = Field(default="zava-response-generator", alias="RESPONSE_AGENT_NAME")

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

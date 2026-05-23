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
    hr_kb_name: str = Field(default="pepsico-hr-kb", alias="HR_KB_NAME")
    hr_kb_source_id: str = Field(default="pepsico-hr-source", alias="HR_KB_SOURCE_ID")
    hr_kb_connection_name: str = Field(default="pepsico-hr-kb-conn", alias="HR_KB_CONNECTION_NAME")
    marketing_kb_name: str = Field(default="pepsico-marketing-kb", alias="MARKETING_KB_NAME")
    marketing_kb_source_id: str = Field(
        default="pepsico-marketing-source", alias="MARKETING_KB_SOURCE_ID"
    )
    marketing_kb_connection_name: str = Field(
        default="pepsico-marketing-kb-conn", alias="MARKETING_KB_CONNECTION_NAME"
    )
    marketing_toolbox_name: str = Field(
        default="pepsico-marketing-tools", alias="MARKETING_TOOLBOX_NAME"
    )

    # ---- Cosmos DB ---------------------------------------------------------
    cosmos_endpoint: str = Field(default="", alias="COSMOS_ENDPOINT")
    cosmos_database: str = Field(default="pepsico", alias="COSMOS_DATABASE")
    cosmos_products_container: str = Field(default="products", alias="COSMOS_PRODUCTS_CONTAINER")
    cosmos_marketing_container: str = Field(
        default="marketing_campaigns", alias="COSMOS_MARKETING_CONTAINER"
    )

    # ---- MCP servers -------------------------------------------------------
    products_mcp_url: str = Field(default="", alias="PRODUCTS_MCP_URL")
    products_mcp_connection_name: str = Field(
        default="pepsico-products-mcp-conn", alias="PRODUCTS_MCP_CONNECTION_NAME"
    )
    marketing_mcp_url: str = Field(default="", alias="MARKETING_MCP_URL")
    marketing_mcp_connection_name: str = Field(
        default="pepsico-marketing-mcp-conn", alias="MARKETING_MCP_CONNECTION_NAME"
    )

    # ---- Bing Grounding ----------------------------------------------------
    bing_grounding_connection_name: str = Field(
        default="pepsico-bing-grounding", alias="BING_GROUNDING_CONNECTION_NAME"
    )

    # ---- Foundry agent names ----------------------------------------------
    hr_agent_name: str = Field(default="pepsico-hr-agent", alias="HR_AGENT_NAME")
    products_agent_name: str = Field(default="pepsico-products-agent", alias="PRODUCTS_AGENT_NAME")
    marketing_agent_name: str = Field(default="pepsico-marketing-agent", alias="MARKETING_AGENT_NAME")
    response_agent_name: str = Field(default="pepsico-response-generator", alias="RESPONSE_AGENT_NAME")

    # ---- Container Apps ----------------------------------------------------
    aca_environment: str = Field(default="pepsico-aca-env", alias="ACA_ENVIRONMENT")
    aca_location: str = Field(default="eastus2", alias="ACA_LOCATION")
    acr_name: str = Field(default="", alias="ACR_NAME")

    # ---- Observability -----------------------------------------------------
    applicationinsights_connection_string: str = Field(
        default="", alias="APPLICATIONINSIGHTS_CONNECTION_STRING"
    )
    otel_service_name: str = Field(default="pepsico-agents-workshop", alias="OTEL_SERVICE_NAME")


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()

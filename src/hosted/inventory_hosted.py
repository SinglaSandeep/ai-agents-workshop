"""Zava Inventory Insights — Foundry **hosted** agent.

This is the hosted-agent counterpart of the declarative Prompt Agent in
``src/foundry_agents/create_inventory_agent.py``. Instead of registering a
``PromptAgentDefinition`` (model + instructions + an ``MCPTool``) with Foundry,
this module builds a real Agent Framework :class:`~agent_framework.Agent`,
attaches the Zava Inventory MCP server as an ``MCPStreamableHTTPTool``, and
serves it over the OpenAI-compatible Responses API with
:class:`~agent_framework_foundry_hosting.ResponsesHostServer`.

Modeled on the Azure-Samples ``stage4_foundry_hosted.py`` demo:
https://github.com/Azure-Samples/foundry-hosted-agentframework-demos/blob/main/agents/stage4_foundry_hosted.py

Run locally (serves the Responses API on the port Foundry/azd injects):
    python -m src.hosted.inventory_hosted

Deploy: build the Docker image (``src/hosted/Dockerfile``), push to ACR, then
register it as a Foundry agent version (see ``docs/11_hosted_agents``).
"""

from __future__ import annotations

import logging
from collections.abc import Awaitable, Callable

from agent_framework import Agent, MCPStreamableHTTPTool
from agent_framework._middleware import ChatContext
from agent_framework._types import ChatResponse, Message
from agent_framework.foundry import FoundryChatClient
from agent_framework.observability import enable_instrumentation
from agent_framework_foundry_hosting import ResponsesHostServer
from agent_framework_openai._exceptions import OpenAIContentFilterException
from azure.identity import (
    AzureDeveloperCliCredential,
    ChainedTokenCredential,
    ManagedIdentityCredential,
)

from src.common.settings import get_settings
from src.prompts import load_prompt

logger = logging.getLogger("zava-inventory-hosted")

# The Inventory agent's behaviour lives in the same Prompty file the declarative
# Prompt Agent uses, so the two hosting models stay in lock-step.
INSTRUCTIONS = load_prompt("inventory_agent")

# Stable, dot-free tool name (the hosted Responses API rejects dotted tool ids).
INVENTORY_TOOL_NAME = "zava_inventory"

CONTENT_FILTER_MESSAGE = (
    "I can't help with that request because it violates content safety "
    "policies. If you have a safer or policy-compliant version of the "
    "question, I can help with that instead."
)


async def content_filter_middleware(
    context: ChatContext, call_next: Callable[[], Awaitable[None]]
) -> None:
    """Convert model-side content-filter blocks into a friendly refusal."""
    try:
        await call_next()
    except OpenAIContentFilterException:
        logger.info("Returning friendly refusal for content-filtered prompt")
        context.result = ChatResponse(
            messages=Message("assistant", [CONTENT_FILTER_MESSAGE]),
            finish_reason="stop",
        )


def build_agent() -> Agent:
    """Construct the Zava Inventory hosted agent (model + MCP tool)."""
    settings = get_settings()

    if not settings.azure_ai_project_endpoint:
        raise RuntimeError(
            "AZURE_AI_PROJECT_ENDPOINT is empty. See docs/00_setup."
        )
    if not settings.inventory_mcp_url:
        raise RuntimeError(
            "INVENTORY_MCP_URL is empty. Deploy the Inventory MCP server first."
        )

    # Identity used at runtime. In the Foundry-hosted container this is a
    # managed identity — the **user-assigned** ``id-zava-workload``
    # (APP_IDENTITY_CLIENT_ID) when set, else AZURE_CLIENT_ID, else the
    # system-assigned identity. Locally it falls back to the azd CLI credential.
    hosted_client_id = settings.app_identity_client_id or settings.azure_client_id
    credential = ChainedTokenCredential(
        ManagedIdentityCredential(client_id=hosted_client_id or None),
        AzureDeveloperCliCredential(
            tenant_id=settings.azure_tenant_id or None, process_timeout=60
        ),
    )

    # The Zava Inventory MCP server (Cosmos DB-backed) is anonymous, so no
    # bearer auth is required — just point the streamable-HTTP tool at /mcp.
    logger.info("Using Inventory MCP at %s", settings.inventory_mcp_url)
    inventory_tool = MCPStreamableHTTPTool(
        name=INVENTORY_TOOL_NAME,
        url=settings.inventory_mcp_url,
        load_prompts=False,
    )

    client = FoundryChatClient(
        project_endpoint=settings.azure_ai_project_endpoint,
        model=settings.azure_ai_model_deployment,
        credential=credential,
        middleware=[content_filter_middleware],
    )

    return Agent(
        client=client,
        # Distinct from the declarative Prompt Agent (``inventory_agent_name``)
        # so both can be registered. Magentic still
        # delegates to the Prompt Agent — see src/orchestrator/magentic_router.py.
        name=settings.inventory_hosted_agent_name,
        description=(
            "Zava distributor-inventory insights specialist, **hosted** "
            "(Agent Framework container, MCP-backed by Cosmos DB)."
        ),
        instructions=INSTRUCTIONS,
        tools=[inventory_tool],
        # Hosted agents must stay stateless — the runtime manages history.
        default_options={"store": False},
    )


def main() -> None:
    """Serve the Inventory hosted agent over the Responses API."""
    agent = build_agent()
    server = ResponsesHostServer(agent)
    server.run()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    enable_instrumentation(enable_sensitive_data=True)
    main()

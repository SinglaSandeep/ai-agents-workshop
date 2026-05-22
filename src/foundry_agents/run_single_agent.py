"""Run a single Foundry agent and return its final text answer.

This module is built up across Exercises 03, 05, and 06. In each of those
exercises you will:

1. Create a Foundry hosted agent (Products / Marketing / HR).
2. Implement the matching branch in `run_single_agent` below so the chat app
   can route queries to it.

The reference solution lives in `solution/foundry_agents/run_single_agent.py`.
"""

from __future__ import annotations

from src.common.settings import get_settings


async def run_single_agent(mode: str, query: str) -> str:
    """Send `query` to the Foundry agent matching `mode` and return the text.

    `mode` is one of: ``"products"``, ``"marketing"``, ``"hr"``.
    """

    settings = get_settings()

    # TODO (Exercise 03): map `mode` to the right Foundry agent name.
    #   agent_name = {
    #       "products": settings.products_agent_name,
    #       "marketing": settings.marketing_agent_name,
    #       "hr": settings.hr_agent_name,
    #   }[mode]

    # TODO (Exercise 03): open an AzureAIAgentClient and call the named agent.
    #   from agent_framework import Agent
    #   from agent_framework.azure import AzureAIAgentClient
    #   from azure.identity.aio import DefaultAzureCredential
    #
    #   async with DefaultAzureCredential() as cred:
    #       async with AzureAIAgentClient(
    #           project_endpoint=settings.azure_ai_project_endpoint,
    #           model_deployment_name=settings.azure_ai_model_deployment,
    #           credential=cred,
    #       ) as client:
    #           agent = Agent(
    #               client=client,
    #               name=mode,
    #               agent_reference={"name": agent_name, "type": "agent_reference"},
    #           )
    #           response = await agent.run(query)
    #           return response.text

    raise NotImplementedError(
        f"run_single_agent('{mode}', ...) is not implemented yet. "
        "Complete Exercise 03 to wire in the Products agent."
    )

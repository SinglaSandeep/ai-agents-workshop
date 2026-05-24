"""Run a single Foundry agent and return its final text answer.

Uses `agent_framework.foundry.FoundryAgent` (agent-framework 1.6.x), which
references a hosted agent in Microsoft Foundry by name. The Foundry SDK
loads the agent's definition (model + instructions + tools) automatically.
"""

from __future__ import annotations

from src.common.settings import get_settings


async def run_single_agent(mode: str, query: str) -> str:
    settings = get_settings()

    agent_name = {
        "products": settings.products_agent_name,
        "marketing": settings.marketing_agent_name,
        "hr": settings.hr_agent_name,
    }[mode]

    # Lazy import — only require agent-framework when this code runs.
    from agent_framework.foundry import FoundryAgent
    from azure.identity.aio import DefaultAzureCredential

    async with DefaultAzureCredential() as cred:
        async with FoundryAgent(
            project_endpoint=settings.azure_ai_project_endpoint,
            agent_name=agent_name,
            credential=cred,
        ) as agent:
            response = await agent.run(query)
            return getattr(response, "text", str(response))

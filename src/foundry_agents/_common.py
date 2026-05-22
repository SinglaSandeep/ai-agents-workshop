"""Shared helpers used by the agent-creation scripts in this package.

Every `create_*_agent.py` script in this folder follows the same shape:

1. Compose `PromptAgentDefinition` (model + instructions + tools).
2. Call `project_client.agents.create_version(...)`.
3. Print the agent name and version so subsequent scripts can re-use them.

These helpers centralise the boilerplate so each script stays focused on
*what makes that agent different* (its tools and its instructions).
"""

from __future__ import annotations

import logging

from azure.ai.projects.models import PromptAgentDefinition

from src.common.foundry_client import get_project_client
from src.common.settings import get_settings

LOG = logging.getLogger(__name__)


def create_or_update_agent(
    *,
    agent_name: str,
    instructions: str,
    tools: list,
    description: str | None = None,
    model: str | None = None,
):
    """Create a new **version** of the named Foundry agent."""
    settings = get_settings()
    project = get_project_client()

    definition = PromptAgentDefinition(
        model=model or settings.azure_ai_model_deployment,
        instructions=instructions,
        tools=tools,
    )

    LOG.info("Creating agent version: %s (model=%s, tools=%d)", agent_name, definition.model, len(tools))
    agent = project.agents.create_version(
        agent_name=agent_name,
        definition=definition,
        description=description,
    )
    LOG.info("Created agent '%s' version '%s'", agent.name, agent.version)
    return agent

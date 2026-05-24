"""Launch Agent Framework DevUI with the Pepsico specialist agents.

Replaces the legacy FastAPI / chat.html frontend. DevUI auto-generates a
browser UI plus an OpenAI-compatible Responses API at
``/v1/responses``, so you can:

* chat with each agent in the browser at http://127.0.0.1:8080
* invoke them programmatically via the standard OpenAI Python SDK
  (``metadata={"entity_id": "<agent_name>"}``)

All three specialists are referenced from Microsoft Foundry by name —
HR and Products are regular Foundry hosted agents (Exercises 03 and 06),
while Marketing is the Foundry-hosted ``ResponsesHostServer`` container
deployed in Exercise 05 (registered in Foundry under the same name).

Usage:

.. code-block:: powershell

    python -m src.app.devui_launch

Reference: ``agent_framework.devui.serve`` and
https://github.com/Azure-Samples/foundry-hosted-agentframework-demos
"""

from __future__ import annotations

import logging
import os
from typing import Any

from dotenv import load_dotenv

from src.common.settings import get_settings

load_dotenv()

logger = logging.getLogger("pepsico.devui")


def _build_agent(name: str, agent_name: str, description: str, credential: Any) -> Any:
    """Construct a non-context-managed ``FoundryAgent`` for DevUI.

    DevUI manages the agent lifetime itself — per the DevUI README, we
    must NOT wrap agents in ``async with`` (connections would close
    before the first request).
    """
    from agent_framework.foundry import FoundryAgent

    settings = get_settings()
    return FoundryAgent(
        project_endpoint=settings.azure_ai_project_endpoint,
        agent_name=agent_name,
        credential=credential,
        name=name,
        description=description,
    )


def main() -> None:
    settings = get_settings()

    # Lazy imports — only required when DevUI actually runs.
    from agent_framework.devui import register_cleanup, serve
    from azure.identity import DefaultAzureCredential

    # Sync DefaultAzureCredential — FoundryAgent accepts both sync and
    # async credential types, and DevUI registers a cleanup hook to
    # close it on shutdown.
    credential = DefaultAzureCredential(exclude_interactive_browser_credential=False)

    entities: list[Any] = []

    specs = [
        (
            "products",
            settings.products_agent_name,
            "Pepsico product catalog (SKU, brand, size, calories, price). Backed by the Products MCP server.",
        ),
        (
            "marketing",
            settings.marketing_agent_name,
            "Pepsico marketing campaigns (status, KPIs, budgets, ROI). Backed by the Foundry-hosted Marketing agent + Marketing MCP server.",
        ),
        (
            "hr",
            settings.hr_agent_name,
            "Pepsico HR policy and benefits. Grounded in the Foundry IQ knowledge base.",
        ),
    ]

    for name, agent_name, description in specs:
        if not agent_name:
            logger.warning("Skipping %s — no agent name configured in settings.", name)
            continue
        try:
            agent = _build_agent(name, agent_name, description, credential)
            entities.append(agent)
            logger.info("Registered %s -> Foundry agent %r", name, agent_name)
        except Exception:  # pragma: no cover - best-effort registration
            logger.exception("Failed to construct DevUI entity for %s", name)

    if not entities:
        raise RuntimeError(
            "No Foundry agents could be registered. Have you completed "
            "Exercise 03 (Products) yet? Check `AZURE_AI_PROJECT_ENDPOINT` "
            "and the *_AGENT_NAME settings in your .env file."
        )

    # Close the shared credential on DevUI shutdown.
    register_cleanup(entities[0], credential.close)

    port = int(os.getenv("DEVUI_PORT", "8080"))
    host = os.getenv("DEVUI_HOST", "127.0.0.1")
    instrumentation = os.getenv("DEVUI_INSTRUMENTATION", "false").lower() in {
        "1",
        "true",
        "yes",
    }

    logger.info("Launching DevUI on http://%s:%d with %d agents", host, port, len(entities))
    serve(
        entities=entities,
        host=host,
        port=port,
        auto_open=True,
        instrumentation_enabled=instrumentation,
        # Local-only bind, so no token required.
        auth_enabled=False,
    )


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")
    main()

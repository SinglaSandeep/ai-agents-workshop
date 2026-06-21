"""Register the Zava Inventory **hosted** agent as a Foundry agent version.

This is "part 4" of the no-azd hosted deploy flow, in code (the counterpart of
``azd ai agent deploy`` in the Azure-Samples ``foundry-hosted-agentframework``
demo). It points a Foundry **HostedAgentDefinition** at a container image that
already lives in ACR (built by ``scripts/deploy-inventory-hosted.ps1``) and
creates a new agent version that runs it behind the Responses API.

The container entrypoint is ``src/hosted/inventory_hosted.py`` — at runtime it
rebuilds the same Agent Framework agent from the environment variables injected
here, so this script only declares *how* Foundry should run the image (image
ref, CPU/memory, protocol, env vars).

Usage (run from the repo root)::

    python scripts/register_inventory_hosted.py            # uses .env / settings
    python scripts/register_inventory_hosted.py --image-tag v2
    python scripts/register_inventory_hosted.py --image myacr.azurecr.io/zava-inventory-hosted-agent:latest
"""

from __future__ import annotations

import argparse
import logging
import sys
from pathlib import Path

# Make ``src`` importable when this file is run directly (python scripts/...).
_REPO_ROOT = Path(__file__).resolve().parents[1]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from azure.ai.projects.models import (  # noqa: E402
    AgentProtocol,
    ContainerConfiguration,
    HostedAgentDefinition,
    ProtocolVersionRecord,
)

from src.common.foundry_client import get_project_client  # noqa: E402
from src.common.settings import get_settings  # noqa: E402

LOG = logging.getLogger(__name__)

# The container speaks the OpenAI-compatible Responses API (ResponsesHostServer).
_RESPONSES_PROTOCOL_VERSION = "v0.1.1"


def _default_image(acr_name: str, agent_name: str, tag: str) -> str:
    return f"{acr_name}.azurecr.io/{agent_name}:{tag}"


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--image",
        default=None,
        help="Full image reference. Defaults to "
        "<ACR_NAME>.azurecr.io/<INVENTORY_HOSTED_AGENT_NAME>:<tag>.",
    )
    parser.add_argument("--image-tag", default="latest", help="Image tag (default: latest).")
    parser.add_argument("--cpu", default="1", help="vCPU for the hosted container (default: 1).")
    parser.add_argument(
        "--memory", default="2Gi", help="Memory for the hosted container (default: 2Gi)."
    )
    return parser.parse_args()


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    args = _parse_args()
    settings = get_settings()

    if not settings.azure_ai_project_endpoint:
        raise RuntimeError("AZURE_AI_PROJECT_ENDPOINT is empty. See docs/00_setup.")
    if not settings.inventory_mcp_url:
        raise RuntimeError(
            "INVENTORY_MCP_URL is empty. Deploy the Inventory MCP server first."
        )

    image = args.image
    if not image:
        if not settings.acr_name:
            raise RuntimeError(
                "ACR_NAME is empty. Pass --image or set ACR_NAME in .env."
            )
        image = _default_image(
            settings.acr_name, settings.inventory_hosted_agent_name, args.image_tag
        )

    # Environment the container needs at runtime — inventory_hosted.py reads
    # these via get_settings(). When a user-assigned identity is configured the
    # container runs as it (must already hold the model / Foundry roles and be
    # attached to the Foundry account); otherwise the system-assigned identity.
    env_vars = {
        "AZURE_AI_PROJECT_ENDPOINT": settings.azure_ai_project_endpoint,
        "AZURE_AI_MODEL_DEPLOYMENT": settings.azure_ai_model_deployment,
        "INVENTORY_MCP_URL": settings.inventory_mcp_url,
        "INVENTORY_HOSTED_AGENT_NAME": settings.inventory_hosted_agent_name,
    }
    hosted_client_id = settings.app_identity_client_id or settings.azure_client_id
    if hosted_client_id:
        # The container's ManagedIdentityCredential / DefaultAzureCredential
        # both resolve a user-assigned identity from AZURE_CLIENT_ID.
        env_vars["AZURE_CLIENT_ID"] = hosted_client_id
    if settings.applicationinsights_connection_string:
        env_vars["APPLICATIONINSIGHTS_CONNECTION_STRING"] = (
            settings.applicationinsights_connection_string
        )

    definition = HostedAgentDefinition(
        cpu=args.cpu,
        memory=args.memory,
        container_configuration=ContainerConfiguration(image=image),
        protocol_versions=[
            ProtocolVersionRecord(
                protocol=AgentProtocol.RESPONSES,
                version=_RESPONSES_PROTOCOL_VERSION,
            )
        ],
        environment_variables=env_vars,
    )

    project = get_project_client()
    LOG.info(
        "Registering hosted agent '%s' from image %s (cpu=%s, memory=%s)",
        settings.inventory_hosted_agent_name,
        image,
        args.cpu,
        args.memory,
    )
    agent = project.agents.create_version(
        agent_name=settings.inventory_hosted_agent_name,
        definition=definition,
        description=(
            "Zava distributor-inventory insights specialist, hosted "
            "(Agent Framework container, MCP-backed by Cosmos DB)."
        ),
    )
    LOG.info("Registered hosted agent '%s' version '%s'", agent.name, agent.version)
    print(f"{agent.name} @ version {agent.version}")


if __name__ == "__main__":
    main()

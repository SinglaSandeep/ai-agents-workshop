"""Enable hourly continuous evaluation against live Marketing-agent traces.

Continuous evaluation samples a small fraction of live agent traces and
scores them with the chosen evaluators. Results stream into Application
Insights and the Foundry observability panel.

Usage:
    python -m solution.evaluations.continuous_eval
"""

from __future__ import annotations

import os

from azure.ai.projects import AIProjectClient
from dotenv import load_dotenv

from src.common.foundry_client import get_credential
from src.common.settings import get_settings

load_dotenv(override=True)


def main() -> None:
    settings = get_settings()
    project_client = AIProjectClient(
        endpoint=settings.azure_ai_project_endpoint,
        credential=get_credential(),
    )

    name = os.environ.get("MARKETING_CONTINUOUS_EVAL", "marketing-continuous")

    rule = project_client.evaluations.continuous.create_or_update(
        name=name,
        properties={
            "agentName": settings.marketing_agent_name,
            "samplingPercentage": 10,
            "evaluatorIds": [
                "builtin.task_adherence",
                "builtin.groundedness",
                "builtin.relevance",
            ],
            "modelDeployment": settings.azure_ai_model_deployment,
        },
    )
    print(f"Continuous evaluation enabled: {rule.name}")


if __name__ == "__main__":
    main()

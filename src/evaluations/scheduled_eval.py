"""Register a daily scheduled quality evaluation for the Marketing agent.

Reads the same testing criteria as `quality_eval.py` and submits them as a
recurring schedule via Foundry's evaluation schedules API.

Usage:
    python -m src.evaluations.scheduled_eval
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

    schedule_name = os.environ.get(
        "MARKETING_QUALITY_SCHEDULE", "marketing-quality-daily"
    )

    schedule = project_client.evaluations.schedules.create_or_update(
        name=schedule_name,
        properties={
            "evaluatorIds": [
                "builtin.task_adherence",
                "builtin.groundedness",
                "builtin.relevance",
                "builtin.response_completeness",
            ],
            "target": {
                "type": "azure_ai_agent",
                "name": settings.marketing_agent_name,
                "version": "latest",
            },
            "trigger": {
                "type": "recurrence",
                "frequency": "Day",
                "interval": 1,
            },
            "modelDeployment": settings.azure_ai_model_deployment,
        },
    )
    print(f"Scheduled quality evaluation: {schedule.name}")


if __name__ == "__main__":
    main()

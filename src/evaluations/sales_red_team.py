"""Guardrails: AI Red Teaming scan for the Zava **Sales** Foundry agent.

This is the *Guardrails* exercise. It launches a Foundry **AI Red Teaming**
scan against the deployed Sales agent. The red team automatically generates
adversarial prompts (jailbreaks, prohibited-action probes, prompt-injection
style attacks) and scores the agent's responses with built-in safety
evaluators. Results land in the Foundry **Evaluations** tab so you get evidence
the agent stays in scope and refuses harmful requests *before* customers try.

What it checks
--------------
* **Task Adherence** — does the agent stay on its Zava sales-insights job and
  refuse to be steered off task?
* **Sensitive Data Leakage** — does it avoid exposing data it should not?
* **Self-Harm / Sexual / Violent content** — does it refuse to produce harmful
  content even under adversarial attack strategies?

The flow mirrors the reference sample
``Azure-Samples/foundry-hosted-agentframework-demos/scripts/red_team_scan.py``.

Prerequisites
-------------
* The Sales agent is deployed (``python -m src.foundry_agents.create_sales_agent``).
* ``az login`` against the workshop subscription.
* ``.env`` has ``AZURE_AI_PROJECT_ENDPOINT``, ``AZURE_AI_MODEL_DEPLOYMENT`` and
  ``SALES_AGENT_NAME``.

Usage
-----
    python -m src.evaluations.sales_red_team
"""

from __future__ import annotations

import json
import logging
import os
import time

from azure.ai.projects.models import (
    AgentTaxonomyInput,
    AttackStrategy,
    AzureAIAgentTarget,
    EvaluationTaxonomy,
    RiskCategory,
)

from src.common.foundry_client import get_project_client
from src.common.settings import get_settings

LOG = logging.getLogger(__name__)

_OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "red_team_output")

# Built-in safety evaluators that score each adversarial turn.
SAFETY_EVALUATORS = [
    {"name": "Task Adherence", "evaluator_name": "builtin.task_adherence", "needs_model": True},
    {"name": "Sensitive Data Leakage", "evaluator_name": "builtin.sensitive_data_leakage"},
    {"name": "Self-Harm", "evaluator_name": "builtin.self_harm"},
    {"name": "Sexual Content", "evaluator_name": "builtin.sexual"},
    {"name": "Violent Content", "evaluator_name": "builtin.violence"},
]


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    settings = get_settings()

    agent_name = settings.sales_agent_name
    model_deployment = settings.azure_ai_model_deployment
    os.makedirs(_OUTPUT_DIR, exist_ok=True)

    project_client = get_project_client()

    # 1. Look up the deployed agent and build the red team target. -----------
    agent = project_client.agents.get(agent_name=agent_name)
    agent_version = agent.versions["latest"]
    LOG.info("Red-teaming agent '%s' version '%s'", agent_version.name, agent_version.version)

    target = AzureAIAgentTarget(name=agent_name, version=str(agent_version.version))

    # 2. Create the red team (eval group) with built-in safety evaluators. ---
    testing_criteria = []
    for ev in SAFETY_EVALUATORS:
        criterion = {
            "type": "azure_ai_evaluator",
            "name": ev["name"],
            "evaluator_name": ev["evaluator_name"],
            "evaluator_version": "1",
        }
        if ev.get("needs_model"):
            criterion["initialization_parameters"] = {"deployment_name": model_deployment}
        testing_criteria.append(criterion)

    openai_client = project_client.get_openai_client()
    red_team = openai_client.evals.create(
        name=f"Sales Red Team - {agent_name}",
        data_source_config={"type": "azure_ai_source", "scenario": "red_team"},
        testing_criteria=testing_criteria,
    )
    LOG.info("Created red team: %s", red_team.id)

    # 3. Create a taxonomy of prohibited actions for this agent. -------------
    taxonomy = project_client.beta.evaluation_taxonomies.create(
        name=agent_name,
        taxonomy=EvaluationTaxonomy(
            description=f"Taxonomy for red teaming {agent_name}",
            taxonomy_input=AgentTaxonomyInput(
                risk_categories=[RiskCategory.PROHIBITED_ACTIONS],
                target=target,
            ),
        ),
    )
    LOG.info("Created taxonomy: %s", taxonomy.id)

    # 4. Launch the red team run with a few attack strategies. ---------------
    eval_run = openai_client.evals.runs.create(
        eval_id=red_team.id,
        name=f"Sales Red Team Run - {agent_name}",
        data_source={
            "type": "azure_ai_red_team",
            "item_generation_params": {
                "type": "red_team_taxonomy",
                "attack_strategies": [
                    AttackStrategy.BASELINE,
                    AttackStrategy.URL,
                    AttackStrategy.TENSE,
                ],
                "num_turns": 5,
                "source": {"type": "file_id", "id": taxonomy.id},
            },
            "target": target.as_dict(),
        },
    )
    LOG.info("Created run: %s (status=%s)", eval_run.id, eval_run.status)

    # 5. Poll until the run completes. ---------------------------------------
    print("Polling for completion", end="", flush=True)
    while True:
        run = openai_client.evals.runs.retrieve(run_id=eval_run.id, eval_id=red_team.id)
        if run.status in ("completed", "failed", "canceled"):
            break
        print(".", end="", flush=True)
        time.sleep(10)

    print(f"\nRun finished — status: {run.status}")
    report_url = getattr(run, "report_url", None)
    if report_url:
        print(f"Open the red team report in Foundry: {report_url}")

    # 6. Save the per-item output. -------------------------------------------
    items = list(openai_client.evals.runs.output_items.list(run_id=run.id, eval_id=red_team.id))
    output_path = os.path.join(_OUTPUT_DIR, "sales_red_team_output.json")
    with open(output_path, "w") as f:
        json.dump(
            [item.to_dict() if hasattr(item, "to_dict") else str(item) for item in items],
            f,
            indent=2,
        )
    print(f"Saved {len(items)} output items to {output_path}")


if __name__ == "__main__":
    main()

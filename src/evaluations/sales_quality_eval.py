"""Cloud quality evaluation for the Zava **Sales** Foundry agent.

Runs the **top-3 agent evaluators** against the *deployed* Sales agent and
publishes the results to the Microsoft Foundry **Evaluations** tab:

1. ``builtin.intent_resolution`` — did the agent understand the sales question?
2. ``builtin.tool_call_accuracy`` — did it call the right ``zava-sales`` MCP
   tool with the correct arguments?
3. ``builtin.task_adherence``    — did the final answer follow the Sales
   Specialist system prompt (quantified, 1-3 bullets, tool-only figures)?

This uses the Foundry **cloud** evaluation API (``evals``) so the agent is run
*server-side* against your ground-truth dataset — you do not run the agent
locally. The flow mirrors the reference sample
``Azure-Samples/foundry-hosted-agentframework-demos/scripts/quality_eval.py``
but is scoped to the three evaluators that matter most for this agent.

Prerequisites
-------------
* The Sales agent is deployed (``python -m src.foundry_agents.create_sales_agent``).
* ``az login`` (or ``azd auth login``) against the workshop subscription.
* ``.env`` has ``AZURE_AI_PROJECT_ENDPOINT``, ``AZURE_AI_MODEL_DEPLOYMENT`` and
  ``SALES_AGENT_NAME`` (defaults to ``zava-sales-agent``).

Usage
-----
    python -m src.evaluations.sales_quality_eval
"""

from __future__ import annotations

import json
import logging
import os
import time

from src.common.foundry_client import get_project_client
from src.common.settings import get_settings
from src.evaluations.sales_tool_definitions import SALES_TOOL_DEFINITIONS

LOG = logging.getLogger(__name__)

_HERE = os.path.dirname(__file__)
_DATASET_PATH = os.path.join(_HERE, "eval_data", "sales_ground_truth.jsonl")
_OUTPUT_DIR = os.path.join(_HERE, "eval_output")

# The three evaluators we focus on for the Sales agent. Each is a Foundry
# built-in evaluator referenced by name; ``deployment_name`` is the model that
# acts as the LLM judge.
TOP_3_EVALUATORS = [
    {
        "name": "Intent Resolution",
        "evaluator_name": "builtin.intent_resolution",
        "data_mapping": {
            "query": "{{item.query}}",
            "response": "{{sample.output_items}}",
        },
    },
    {
        "name": "Tool Call Accuracy",
        "evaluator_name": "builtin.tool_call_accuracy",
        "data_mapping": {
            "query": "{{item.query}}",
            "response": "{{sample.output_items}}",
            "tool_definitions": "{{item.tool_definitions}}",
        },
    },
    {
        "name": "Task Adherence",
        "evaluator_name": "builtin.task_adherence",
        "data_mapping": {
            "query": "{{item.query}}",
            "response": "{{sample.output_items}}",
        },
    },
]


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    settings = get_settings()

    agent_name = settings.sales_agent_name
    model_deployment = settings.azure_ai_model_deployment
    os.makedirs(_OUTPUT_DIR, exist_ok=True)

    project_client = get_project_client()

    # 1. Confirm the agent is deployed and grab its latest version. ----------
    agent = project_client.agents.get(agent_name=agent_name)
    agent_version = agent.versions["latest"]
    LOG.info("Evaluating agent '%s' version '%s'", agent_version.name, agent_version.version)

    # 2. Augment the ground-truth file with tool definitions and upload it. ---
    augmented_path = os.path.join(_OUTPUT_DIR, "sales_ground_truth_with_tools.jsonl")
    with open(_DATASET_PATH) as src, open(augmented_path, "w") as dst:
        for line in src:
            line = line.strip()
            if not line:
                continue
            item = json.loads(line)
            item["tool_definitions"] = SALES_TOOL_DEFINITIONS
            dst.write(json.dumps(item) + "\n")

    dataset = project_client.datasets.upload_file(
        name=f"{agent_name}-eval-ground-truth",
        version=str(int(time.time())),
        file_path=augmented_path,
    )
    LOG.info("Uploaded dataset: %s", dataset.id)

    # 3. Build the testing criteria from the top-3 evaluators. ---------------
    testing_criteria = [
        {
            "type": "azure_ai_evaluator",
            "name": ev["name"],
            "evaluator_name": ev["evaluator_name"],
            "data_mapping": ev["data_mapping"],
            "initialization_parameters": {"deployment_name": "gpt-5.4-mini"},
        }
        for ev in TOP_3_EVALUATORS
    ]

    openai_client = project_client.get_openai_client()

    # 4. Create the evaluation (the container for runs). ---------------------
    evaluation = openai_client.evals.create(
        name=f"Sales Quality Evaluation - {agent_name}",
        data_source_config={
            "type": "custom",
            "item_schema": {
                "type": "object",
                "properties": {
                    "query": {"type": "string"},
                    "ground_truth": {"type": "string"},
                    "tool_definitions": {"type": "array"},
                },
                "required": ["query", "ground_truth", "tool_definitions"],
            },
            "include_sample_schema": True,
        },
        testing_criteria=testing_criteria,
    )
    LOG.info("Created evaluation: %s", evaluation.id)

    # 5. Create a run that targets the deployed agent. -----------------------
    eval_run = openai_client.evals.runs.create(
        eval_id=evaluation.id,
        name=f"Sales Quality Eval Run - {agent_name}",
        data_source={
            "type": "azure_ai_target_completions",
            "source": {"type": "file_id", "id": dataset.id},
            "input_messages": {
                "type": "template",
                "template": [
                    {
                        "type": "message",
                        "role": "user",
                        "content": {"type": "input_text", "text": "{{item.query}}"},
                    }
                ],
            },
            "target": {
                "type": "azure_ai_agent",
                "name": agent_name,
                "version": str(agent_version.version),
            },
        },
    )
    LOG.info("Evaluation run started: %s (status=%s)", eval_run.id, eval_run.status)

    # 6. Poll until the run completes. ---------------------------------------
    print("Polling for completion", end="", flush=True)
    while True:
        run = openai_client.evals.runs.retrieve(run_id=eval_run.id, eval_id=evaluation.id)
        if run.status in ("completed", "failed", "canceled"):
            break
        print(".", end="", flush=True)
        time.sleep(10)

    print(f"\nRun finished — status: {run.status}")
    report_url = getattr(run, "report_url", None)
    if report_url:
        print(f"Open the report in Foundry: {report_url}")

    # 7. Save the per-item output for offline inspection. --------------------
    items = list(openai_client.evals.runs.output_items.list(run_id=run.id, eval_id=evaluation.id))
    output_path = os.path.join(_OUTPUT_DIR, "sales_quality_eval_output.json")
    with open(output_path, "w") as f:
        json.dump(
            [item.to_dict() if hasattr(item, "to_dict") else str(item) for item in items],
            f,
            indent=2,
        )
    print(f"Saved {len(items)} output items to {output_path}")


if __name__ == "__main__":
    main()

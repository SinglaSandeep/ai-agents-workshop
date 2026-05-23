"""Run a quality evaluation against the Foundry-hosted Marketing agent.

Adapted from
https://github.com/Azure-Samples/foundry-hosted-agentframework-demos/blob/main/scripts/quality_eval.py
and retargeted at `pepsico-marketing-agent`.

Usage:
    python -m solution.evaluations.quality_eval
"""

from __future__ import annotations

import json
import os
import time
from pathlib import Path

from azure.ai.projects import AIProjectClient
from dotenv import load_dotenv

from src.common.foundry_client import get_credential
from src.common.settings import get_settings

load_dotenv(override=True)

THIS_DIR = Path(__file__).resolve().parent
OUTPUT_DIR = THIS_DIR / "eval_output"
DATASET_PATH = THIS_DIR / "eval_data" / "quality_ground_truth.jsonl"
OUTPUT_DIR.mkdir(exist_ok=True)


# Tool definitions matching the three MCP tools wired in Exercise 05.
TOOL_DEFINITIONS = [
    {
        "name": "marketing_mcp",
        "type": "function",
        "description": "Authoritative Pepsico campaign records (Cosmos-backed MCP).",
        "parameters": {"type": "object", "properties": {}},
    },
    {
        "name": "web_search",
        "type": "function",
        "description": "Foundry Toolbox web search for live web context.",
        "parameters": {
            "type": "object",
            "properties": {"search_query": {"type": "string"}},
            "required": ["search_query"],
        },
    },
    {
        "name": "knowledge_base_retrieve",
        "type": "function",
        "description": "Retrieve marketing briefs from the Foundry IQ KB.",
        "parameters": {
            "type": "object",
            "properties": {
                "queries": {"type": "array", "items": {"type": "string"}}
            },
            "required": ["queries"],
        },
    },
]


def main() -> None:
    settings = get_settings()
    agent_name = settings.marketing_agent_name
    model_deployment = settings.azure_ai_model_deployment
    project_endpoint = settings.azure_ai_project_endpoint

    project_client = AIProjectClient(
        endpoint=project_endpoint, credential=get_credential()
    )

    agent = project_client.agents.get(agent_name=agent_name)
    agent_version = agent.versions["latest"]
    print(f"Agent: {agent_version.name}  version: {agent_version.version}")

    # Augment dataset rows with tool definitions.
    augmented = OUTPUT_DIR / f"quality_ground_truth_with_tools_{agent_name}.jsonl"
    with DATASET_PATH.open() as src, augmented.open("w") as dst:
        for line in src:
            item = json.loads(line)
            item["tool_definitions"] = TOOL_DEFINITIONS
            dst.write(json.dumps(item) + "\n")

    dataset = project_client.datasets.upload_file(
        name=f"{agent_name}-eval-ground-truth",
        version=str(int(time.time())),
        file_path=str(augmented),
    )
    print(f"Uploaded dataset: {dataset.id}")

    def _eval(name: str, evaluator_name: str, mapping: dict) -> dict:
        return {
            "type": "azure_ai_evaluator",
            "name": name,
            "evaluator_name": evaluator_name,
            "data_mapping": mapping,
            "initialization_parameters": {"deployment_name": model_deployment},
        }

    testing_criteria = [
        _eval("Task Adherence", "builtin.task_adherence",
              {"query": "{{item.query}}", "response": "{{sample.output_items}}"}),
        _eval("Task Completion", "builtin.task_completion",
              {"query": "{{item.query}}", "response": "{{sample.output_items}}"}),
        _eval("Intent Resolution", "builtin.intent_resolution",
              {"query": "{{item.query}}", "response": "{{sample.output_items}}"}),
        _eval("Tool Selection", "builtin.tool_selection",
              {"query": "{{item.query}}",
               "response": "{{sample.output_items}}",
               "tool_definitions": "{{item.tool_definitions}}"}),
        _eval("Tool Call Accuracy", "builtin.tool_call_accuracy",
              {"query": "{{item.query}}",
               "response": "{{sample.output_items}}",
               "tool_definitions": "{{item.tool_definitions}}"}),
        _eval("Groundedness", "builtin.groundedness",
              {"query": "{{item.query}}", "response": "{{sample.output_items}}"}),
        _eval("Relevance", "builtin.relevance",
              {"query": "{{item.query}}", "response": "{{sample.output_items}}"}),
        _eval("Response Completeness", "builtin.response_completeness",
              {"ground_truth": "{{item.ground_truth}}",
               "response": "{{sample.output_text}}"}),
    ]

    openai_client = project_client.get_openai_client()

    evaluation = openai_client.evals.create(
        name=f"Quality Evaluation - {agent_name}",
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
    print(f"Created evaluation: {evaluation.id}")

    eval_run = openai_client.evals.runs.create(
        eval_id=evaluation.id,
        name=f"Quality Eval Run - {agent_name}",
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
    print(f"Evaluation run started: {eval_run.id}  status: {eval_run.status}")

    print("Polling for completion", end="", flush=True)
    while True:
        run = openai_client.evals.runs.retrieve(
            run_id=eval_run.id, eval_id=evaluation.id
        )
        if run.status in ("completed", "failed", "canceled"):
            break
        print(".", end="", flush=True)
        time.sleep(10)
    print(f"\nRun finished — status: {run.status}")
    if getattr(run, "report_url", None):
        print(f"Report URL: {run.report_url}")

    items = list(
        openai_client.evals.runs.output_items.list(
            run_id=run.id, eval_id=evaluation.id
        )
    )
    output_path = OUTPUT_DIR / f"quality_eval_output_{agent_name}.json"
    with output_path.open("w") as f:
        json.dump(
            [item.to_dict() if hasattr(item, "to_dict") else str(item) for item in items],
            f,
            indent=2,
        )
    print(f"Output items ({len(items)}) saved to {output_path}")


if __name__ == "__main__":
    main()

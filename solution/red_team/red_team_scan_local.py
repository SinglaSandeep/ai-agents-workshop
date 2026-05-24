"""Local-preview red-team scan against the hosted Marketing agent.

Adapted from
https://github.com/Azure-Samples/foundry-hosted-agentframework-demos/blob/main/scripts/red_team_scan_local.py
and retargeted at the local `azd ai agent run` of `zava-marketing-agent`.

Usage:
    1. cd src/foundry_agents/marketing_hosted && azd ai agent run
    2. python -m solution.red_team.red_team_scan_local
    3. python -m solution.red_team.red_team_scan_local --show-results
"""

from __future__ import annotations

import argparse
import asyncio
import datetime
import json
import os
import pathlib
import urllib.error
import urllib.request

from azure.ai.evaluation.red_team import AttackStrategy, RedTeam, RiskCategory
from azure.identity import AzureDeveloperCliCredential
from dotenv import load_dotenv
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

load_dotenv(override=True)

console = Console()

OUTPUT_DIR = pathlib.Path(__file__).parent / "red_team_output"
OUTPUT_DIR.mkdir(exist_ok=True)

PROJECT_ENDPOINT = os.environ["AZURE_AI_PROJECT_ENDPOINT"]
LOCAL_AGENT_RESPONSES_URL = "http://localhost:8088/responses"


def invoke_local_agent(query: str) -> str:
    body = json.dumps(
        {"input": [{"role": "user", "content": query}], "store": False}
    ).encode("utf-8")
    req = urllib.request.Request(
        LOCAL_AGENT_RESPONSES_URL,
        data=body,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=120) as resp:
            payload = json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        return f"Local agent invocation failed: HTTP {exc.code}: {exc.read().decode('utf-8', errors='replace')}"
    except OSError as exc:
        return f"Local agent invocation failed: {exc}"

    if payload.get("status") == "completed":
        chunks: list[str] = []
        for item in payload.get("output", []):
            for content_item in item.get("content", []):
                text = content_item.get("text")
                if text:
                    chunks.append(text)
        if chunks:
            return "\n".join(chunks).strip()

    err = payload.get("error", {})
    return f"Local agent invocation failed: {err.get('message') or payload.get('status')}"


def render_summary(results_file: pathlib.Path) -> None:
    with results_file.open() as fh:
        results = json.load(fh)

    counts = results.get("result_counts", {})
    console.print(
        Panel.fit(
            f"[bold]Run:[/bold] {results.get('name', 'Unknown')}\n"
            f"[bold]Status:[/bold] {results.get('status', 'Unknown')}\n"
            f"[bold]Total prompts:[/bold] {counts.get('total', 0)}\n"
            f"[bold green]Passed:[/bold green] {counts.get('passed', 0)}   "
            f"[bold red]Failed:[/bold red] {counts.get('failed', 0)}   "
            f"[bold yellow]Errored:[/bold yellow] {counts.get('errored', 0)}",
            title="Marketing red-team scan summary",
        )
    )

    risk_table = Table(title="Risk Category Summary")
    risk_table.add_column("Risk Category")
    risk_table.add_column("Passed", justify="right")
    risk_table.add_column("Failed", justify="right")

    attack_table = Table(title="Attack Strategy Summary")
    attack_table.add_column("Attack Strategy")
    attack_table.add_column("Passed", justify="right")
    attack_table.add_column("Failed", justify="right")

    for criterion in results.get("per_testing_criteria_results", []):
        strategy = str(criterion.get("attack_strategy", "-"))
        criteria = str(criterion.get("testing_criteria", ""))
        row = [str(criterion.get("passed", 0)), str(criterion.get("failed", 0))]
        if strategy == "-":
            risk_table.add_row(criteria, *row)
        else:
            attack_table.add_row(strategy, *row)

    console.print(risk_table)
    console.print(attack_table)


async def run_local_red_team() -> None:
    credential = AzureDeveloperCliCredential(
        tenant_id=os.environ["AZURE_TENANT_ID"]
    )
    red_team = RedTeam(
        azure_ai_project=PROJECT_ENDPOINT,
        credential=credential,
        risk_categories=[
            RiskCategory.Violence,
            RiskCategory.HateUnfairness,
            RiskCategory.Sexual,
            RiskCategory.SelfHarm,
        ],
        num_objectives=2,
    )

    preflight = invoke_local_agent("What is the budget of CMP-2026-001?")
    if preflight.startswith("Local agent invocation failed:"):
        raise RuntimeError(
            "Local agent preflight failed. Start the agent in another terminal "
            "with `azd ai agent run` first.\nDetails: " + preflight
        )

    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    output_path = OUTPUT_DIR / f"local_redteam_output_{timestamp}"

    await red_team.scan(
        scan_name=f"Marketing red team {timestamp}",
        output_path=str(output_path),
        attack_strategies=[
            AttackStrategy.Baseline,
            AttackStrategy.Url,
            AttackStrategy.Tense,
        ],
        target=invoke_local_agent,
    )

    console.print(f"Local red-team results saved to [bold]{output_path}[/bold]")
    results_file = output_path / "results.json"
    if results_file.exists():
        render_summary(results_file)


def show_latest(results_dir: pathlib.Path | None = None) -> None:
    if results_dir is None:
        candidates = sorted(OUTPUT_DIR.glob("local_redteam_output_*/"))
        if not candidates:
            console.print("[red]No red-team output found in[/red]", str(OUTPUT_DIR))
            return
        results_dir = candidates[-1]
    results_file = results_dir / "results.json"
    if not results_file.exists():
        console.print(f"[red]No results.json in[/red] {results_dir}")
        return
    render_summary(results_file)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Local red-team scan for the hosted Marketing agent."
    )
    parser.add_argument(
        "--show-results",
        nargs="?",
        const="latest",
        metavar="RESULTS_DIR",
        help="Show results from a previous scan.",
    )
    args = parser.parse_args()

    if args.show_results is not None:
        if args.show_results == "latest":
            show_latest()
        else:
            show_latest(pathlib.Path(args.show_results))
    else:
        asyncio.run(run_local_red_team())


if __name__ == "__main__":
    main()

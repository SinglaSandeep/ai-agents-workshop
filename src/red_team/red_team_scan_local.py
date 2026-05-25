"""Red-team scan against the registered Marketing Foundry Prompt Agent.

Uses `azure-ai-evaluation[redteam]`'s `RedTeam` orchestrator. The target is
the `zava-marketing-agent` Foundry Prompt Agent you registered in
Exercise 05 (`python -m src.foundry_agents.create_marketing_agent`).

Usage:
    python -m src.red_team.red_team_scan_local
    python -m src.red_team.red_team_scan_local --show-results
"""

from __future__ import annotations

import argparse
import asyncio
import datetime
import json
import os
import pathlib

from azure.ai.evaluation.red_team import AttackStrategy, RedTeam, RiskCategory
from azure.identity import AzureDeveloperCliCredential
from azure.identity.aio import DefaultAzureCredential
from dotenv import load_dotenv
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from src.common.settings import get_settings

load_dotenv(override=True)

console = Console()

OUTPUT_DIR = pathlib.Path(__file__).parent / "red_team_output"
OUTPUT_DIR.mkdir(exist_ok=True)

PROJECT_ENDPOINT = os.environ["AZURE_AI_PROJECT_ENDPOINT"]


async def _invoke_agent_async(query: str) -> str:
    """Run a single turn against the Marketing Foundry Prompt Agent."""
    settings = get_settings()
    from agent_framework.foundry import FoundryAgent

    async with DefaultAzureCredential() as cred:
        async with FoundryAgent(
            project_endpoint=settings.azure_ai_project_endpoint,
            agent_name=settings.marketing_agent_name,
            credential=cred,
        ) as agent:
            response = await agent.run(query)
            return getattr(response, "text", str(response))


def invoke_marketing_agent(query: str) -> str:
    """Sync wrapper used as the RedTeam `target` callback."""
    try:
        return asyncio.run(_invoke_agent_async(query))
    except Exception as exc:  # noqa: BLE001
        return f"Marketing agent invocation failed: {exc}"


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


async def run_red_team() -> None:
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

    preflight = invoke_marketing_agent("What is the budget of CMP-2026-001?")
    if preflight.startswith("Marketing agent invocation failed:"):
        raise RuntimeError(
            "Marketing agent preflight failed. Register it first with "
            "`python -m src.foundry_agents.create_marketing_agent`.\n"
            "Details: " + preflight
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
        target=invoke_marketing_agent,
    )

    console.print(f"Red-team results saved to [bold]{output_path}[/bold]")
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
        description="Red-team scan for the Marketing Foundry Prompt Agent."
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
        asyncio.run(run_red_team())


if __name__ == "__main__":
    main()

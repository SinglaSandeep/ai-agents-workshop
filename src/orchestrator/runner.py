"""CLI entry point to exercise the Magentic orchestrator from the terminal."""

from __future__ import annotations

import argparse
import asyncio
import json
import logging

from .magentic_router import run_query


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    parser = argparse.ArgumentParser(description="Run a query through the Zava Magentic orchestrator.")
    parser.add_argument("--query", required=True, help="The user question.")
    parser.add_argument("--json", action="store_true", help="Emit the full result as JSON.")
    args = parser.parse_args()

    result = asyncio.run(run_query(args.query))

    if args.json:
        print(
            json.dumps(
                {
                    "final_answer": result.final_answer,
                    "plan": result.plan,
                    "transcripts": result.transcripts,
                    "events": result.events,
                },
                indent=2,
            )
        )
    else:
        print("\n=== Plan ===")
        print(" -> ".join(result.plan) or "(no plan)")
        print("\n=== Final Answer ===")
        print(result.final_answer)


if __name__ == "__main__":
    main()

from __future__ import annotations

import argparse
import json

from dotenv import load_dotenv

from .agents import LocalOrchestrator
from .observability import configure_observability, trace_span


def main() -> None:
    load_dotenv()
    parser = argparse.ArgumentParser(description="Run the local AI agents workshop app.")
    parser.add_argument("--query", default="What is the PTO policy?", help="Question to ask an agent.")
    parser.add_argument(
        "--agent",
        choices=["auto", "hr", "products", "marketing"],
        default="auto",
        help="Use auto routing or call one specialist directly.",
    )
    parser.add_argument("--json", action="store_true", help="Print the response as JSON.")
    args = parser.parse_args()

    configure_observability()
    orchestrator = LocalOrchestrator()

    with trace_span("cli.agent_query", agent=args.agent, query=args.query):
        if args.agent == "auto":
            result = orchestrator.answer(args.query)
        else:
            result = orchestrator.answer_with_agent(args.agent, args.query)

    payload = {
        "route": result.route,
        "answer": result.answer,
        "confidence": round(result.confidence, 2),
        "sources": result.sources,
        "considered_agents": result.considered_agents,
    }

    if args.json:
        print(json.dumps(payload, indent=2))
        return

    print(f"Route: {payload['route']}")
    print(f"Confidence: {payload['confidence']}")
    print(f"Answer: {payload['answer']}")
    print(f"Sources: {', '.join(payload['sources']) or 'none'}")


if __name__ == "__main__":
    main()

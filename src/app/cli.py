"""Thin CLI wrapper around the orchestrator runner."""

from __future__ import annotations

from src.orchestrator.runner import main as _orchestrator_main


def main() -> None:
    _orchestrator_main()


if __name__ == "__main__":
    main()

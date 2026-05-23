"""DEPRECATED — Marketing agent moved to Foundry-hosted in Exercise 05.

The Marketing specialist is now a Foundry **hosted agent** built on
Microsoft Agent Framework and deployed via `azd ai agent up`. See:

  - docs/05_marketing_foundry_agent/05_marketing_foundry_agent.md
  - src/foundry_agents/marketing_hosted/
"""

from __future__ import annotations

import sys


def main() -> None:
    sys.stderr.write(
        "create_marketing_agent.py is deprecated.\n"
        "Marketing is now a Foundry-hosted agent. Run:\n"
        "  cd src/foundry_agents/marketing_hosted && azd ai agent up\n"
    )
    sys.exit(2)


if __name__ == "__main__":
    main()

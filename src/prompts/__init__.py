"""Agent prompt texts — one Prompty file per Foundry agent.

Keeping the instruction text in ``src/prompts/<name>.prompty`` (instead of
inline Python strings) makes the prompts easy to read, diff, and tweak without
touching the agent-creation code. Each file uses the Prompty format: a small
YAML front-matter block followed by a ``system:`` message that holds the
agent's instructions.
"""

from __future__ import annotations

import re
from pathlib import Path

_PROMPTS_DIR = Path(__file__).parent

# Strip a leading ``---`` ... ``---`` YAML front-matter block.
_FRONT_MATTER_RE = re.compile(r"\A---\s*\n.*?\n---\s*\n", re.DOTALL)
# Strip a leading Prompty role marker (``system:``/``user:``/``assistant:``).
_ROLE_MARKER_RE = re.compile(r"\A\s*(?:system|user|assistant)\s*:\s*\n", re.IGNORECASE)


def load_prompt(name: str) -> str:
    """Return the system-instruction text for the named agent prompt.

    ``name`` is the file stem under ``src/prompts`` (e.g. ``"sales_agent"``).
    The Prompty front matter and ``system:`` role marker are stripped, leaving
    just the instruction body.
    """
    text = (_PROMPTS_DIR / f"{name}.prompty").read_text(encoding="utf-8")
    text = _FRONT_MATTER_RE.sub("", text, count=1)
    text = _ROLE_MARKER_RE.sub("", text, count=1)
    return text.strip()

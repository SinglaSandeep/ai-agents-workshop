from __future__ import annotations

import os
import re
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class AgentResult:
    agent: str
    answer: str
    confidence: float
    sources: list[str]


@dataclass(frozen=True)
class KnowledgeAgent:
    name: str
    description: str
    keywords: tuple[str, ...]
    knowledge_path: Path

    def score(self, query: str) -> float:
        query_terms = set(_terms(query))
        keyword_hits = sum(1 for keyword in self.keywords if keyword.lower() in query.lower())
        source_terms = set(_terms(self.knowledge_path.read_text(encoding="utf-8")))
        overlap = len(query_terms & source_terms)
        return keyword_hits * 3 + overlap

    def answer(self, query: str) -> AgentResult:
        snippets = _rank_snippets(self.knowledge_path.read_text(encoding="utf-8"), query)
        max_snippets = int(os.getenv("WORKSHOP_MAX_SNIPPETS", "2"))
        selected = snippets[:max_snippets]
        body = " ".join(snippet.text for snippet in selected)
        if not body:
            body = (
                f"I am the {self.name} agent. I do not have enough local knowledge to answer "
                "that confidently yet. Add more source content to this agent's knowledge file."
            )
        sources = [f"{self.knowledge_path.name}#{snippet.heading}" for snippet in selected]
        confidence = min(1.0, self.score(query) / 10)
        return AgentResult(agent=self.name, answer=body, confidence=confidence, sources=sources)


@dataclass(frozen=True)
class KnowledgeSnippet:
    heading: str
    text: str
    score: int


def knowledge_dir() -> Path:
    return Path(__file__).resolve().parents[1] / "knowledge"


def _rank_snippets(markdown: str, query: str) -> list[KnowledgeSnippet]:
    query_terms = set(_terms(query))
    sections = _sections(markdown)
    ranked = []
    for heading, text in sections:
        section_terms = set(_terms(f"{heading} {text}"))
        score = len(query_terms & section_terms)
        if any(term in heading.lower() for term in query_terms):
            score += 2
        if score > 0:
            ranked.append(KnowledgeSnippet(heading=_anchor(heading), text=text, score=score))
    return sorted(ranked, key=lambda snippet: snippet.score, reverse=True)


def _sections(markdown: str) -> list[tuple[str, str]]:
    matches = list(re.finditer(r"^##\s+(.+)$", markdown, flags=re.MULTILINE))
    sections = []
    for index, match in enumerate(matches):
        start = match.end()
        end = matches[index + 1].start() if index + 1 < len(matches) else len(markdown)
        text = " ".join(line.strip() for line in markdown[start:end].splitlines() if line.strip())
        sections.append((match.group(1), text))
    return sections


def _terms(text: str) -> list[str]:
    return [term for term in re.findall(r"[a-zA-Z][a-zA-Z0-9]+", text.lower()) if len(term) > 2]


def _anchor(heading: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", heading.lower()).strip("-")

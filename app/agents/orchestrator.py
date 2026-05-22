from __future__ import annotations

from dataclasses import dataclass

from .base import AgentResult, KnowledgeAgent
from .hr import create_hr_agent
from .marketing import create_marketing_agent
from .products import create_products_agent


@dataclass(frozen=True)
class RoutedResult:
    route: str
    answer: str
    confidence: float
    sources: list[str]
    considered_agents: dict[str, float]


class LocalOrchestrator:
    def __init__(self, agents: list[KnowledgeAgent] | None = None) -> None:
        self.agents = agents or [create_hr_agent(), create_products_agent(), create_marketing_agent()]

    def route(self, query: str) -> KnowledgeAgent:
        scores = {agent.name: agent.score(query) for agent in self.agents}
        best_agent_name = max(scores, key=scores.get)
        return next(agent for agent in self.agents if agent.name == best_agent_name)

    def answer(self, query: str) -> RoutedResult:
        scores = {agent.name: agent.score(query) for agent in self.agents}
        agent = self.route(query)
        result: AgentResult = agent.answer(query)
        return RoutedResult(
            route=result.agent,
            answer=result.answer,
            confidence=result.confidence,
            sources=result.sources,
            considered_agents=scores,
        )

    def answer_with_agent(self, agent_name: str, query: str) -> RoutedResult:
        agent = next((candidate for candidate in self.agents if candidate.name == agent_name), None)
        if agent is None:
            valid_agents = ", ".join(candidate.name for candidate in self.agents)
            raise ValueError(f"Unknown agent '{agent_name}'. Choose one of: {valid_agents}")
        result = agent.answer(query)
        return RoutedResult(
            route=result.agent,
            answer=result.answer,
            confidence=result.confidence,
            sources=result.sources,
            considered_agents={candidate.name: candidate.score(query) for candidate in self.agents},
        )

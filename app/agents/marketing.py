from .base import KnowledgeAgent, knowledge_dir


def create_marketing_agent() -> KnowledgeAgent:
    return KnowledgeAgent(
        name="marketing",
        description="Answers campaign, brand, audience, and channel strategy questions.",
        keywords=("marketing", "campaign", "brand", "audience", "email", "social", "segment", "offer"),
        knowledge_path=knowledge_dir() / "marketing.md",
    )

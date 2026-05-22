from .base import KnowledgeAgent, knowledge_dir


def create_hr_agent() -> KnowledgeAgent:
    return KnowledgeAgent(
        name="hr",
        description="Answers employee policy, PTO, benefits, handbook, and remote work questions.",
        keywords=("hr", "pto", "benefits", "handbook", "employee", "remote", "policy", "leave"),
        knowledge_path=knowledge_dir() / "hr.md",
    )

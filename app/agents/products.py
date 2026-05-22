from .base import KnowledgeAgent, knowledge_dir


def create_products_agent() -> KnowledgeAgent:
    return KnowledgeAgent(
        name="products",
        description="Answers product catalog, pricing, warranty, and device specification questions.",
        keywords=("product", "products", "catalog", "price", "pricing", "watch", "bottle", "hub", "warranty"),
        knowledge_path=knowledge_dir() / "products.md",
    )

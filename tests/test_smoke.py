"""Workshop smoke tests — none require live Azure resources."""

from __future__ import annotations

import json
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_pyproject_lists_required_extras() -> None:
    content = (ROOT / "pyproject.toml").read_text(encoding="utf-8")
    for extra in ("mcp", "framework", "observability", "dev"):
        assert f"{extra} = [" in content, f"Missing extra: {extra}"


def test_env_sample_documents_every_setting() -> None:
    env_sample = (ROOT / ".env.sample").read_text(encoding="utf-8")
    required = [
        "AZURE_AI_PROJECT_ENDPOINT",
        "AZURE_AI_MODEL_DEPLOYMENT",
        "AZURE_AI_PROJECT_RESOURCE_ID",
        "AZURE_SEARCH_ENDPOINT",
        "HR_KB_NAME",
        "COSMOS_ENDPOINT",
        "COSMOS_PRODUCTS_CONTAINER",
        "COSMOS_MARKETING_CONTAINER",
        "PRODUCTS_MCP_URL",
        "MARKETING_MCP_URL",
        "BING_GROUNDING_CONNECTION_NAME",
    ]
    for key in required:
        assert key in env_sample, f"{key} not documented in .env.sample"


def test_products_seed_is_well_formed() -> None:
    path = ROOT / "src" / "mcp_servers" / "products" / "seed" / "products_seed.json"
    data = json.loads(path.read_text(encoding="utf-8"))
    assert len(data) >= 10
    for product in data:
        assert {"id", "name", "brand", "category", "price_usd"} <= set(product)


def test_marketing_seed_is_well_formed() -> None:
    path = ROOT / "src" / "mcp_servers" / "marketing" / "seed" / "marketing_seed.json"
    data = json.loads(path.read_text(encoding="utf-8"))
    assert len(data) >= 5
    for campaign in data:
        assert {"id", "campaign_name", "brand", "status"} <= set(campaign)


def test_hr_knowledge_seed_present() -> None:
    folder = ROOT / "src" / "knowledge_seed" / "hr"
    md_files = list(folder.glob("*.md"))
    assert len(md_files) >= 3


def test_docs_index_and_exercises_exist() -> None:
    docs = ROOT / "docs"
    assert (docs / "00_setup" / "00_setup.md").exists()
    for ex_num in ("01", "02", "03", "04", "05", "06", "07", "08", "09"):
        folders = list(docs.glob(f"{ex_num}_*"))
        assert folders, f"Missing exercise folder for {ex_num}"


def test_dockerfiles_exist_and_reference_correct_module() -> None:
    products_df = (ROOT / "src" / "mcp_servers" / "products" / "Dockerfile").read_text(encoding="utf-8")
    marketing_df = (ROOT / "src" / "mcp_servers" / "marketing" / "Dockerfile").read_text(encoding="utf-8")
    assert "src.mcp_servers.products.server:app" in products_df
    assert "src.mcp_servers.marketing.server:app" in marketing_df


def test_settings_module_importable() -> None:
    # Importable without a populated .env (defaults handle missing values).
    os.environ.setdefault("AZURE_AI_MODEL_DEPLOYMENT", "gpt-4.1-mini")
    from src.common.settings import get_settings

    settings = get_settings()
    assert settings.azure_ai_model_deployment

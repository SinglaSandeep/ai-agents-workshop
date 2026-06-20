"""OpenAI-style tool definitions for the ``zava-sales`` MCP tools.

The Foundry **Tool Call Accuracy** evaluator needs to know which tools the agent
*could* have called so it can judge whether the agent picked the right one with
the right arguments. The deployed Sales agent reaches these tools over MCP, but
the evaluator expects the function-calling JSON schema below.

Keep this list in sync with ``src/mcp_servers/sales/server.py``.
"""

from __future__ import annotations

# Each entry follows the OpenAI function-tool schema understood by the
# ``builtin.tool_call_accuracy`` / ``builtin.tool_selection`` evaluators.
SALES_TOOL_DEFINITIONS: list[dict] = [
    {
        "name": "list_dimensions",
        "type": "function",
        "description": (
            "List the distinct sales dimensions available (stores, regions, "
            "categories, channels, months, segments). Call first when unsure "
            "which filter values are valid."
        ),
        "parameters": {"type": "object", "properties": {}},
    },
    {
        "name": "revenue_summary",
        "type": "function",
        "description": (
            "Aggregate total revenue, units, margin and order count grouped by "
            "one dimension. The primary insight tool."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "group_by": {
                    "type": "string",
                    "description": (
                        "Dimension to aggregate by: store_id, region, category, "
                        "channel, customer_segment, month, or product_id."
                    ),
                },
                "limit": {
                    "type": "integer",
                    "description": "Maximum grouped rows to return (1-200). Default 50.",
                },
            },
        },
    },
    {
        "name": "monthly_trend",
        "type": "function",
        "description": (
            "Return revenue/units/margin per month (ascending), optionally "
            "filtered by category and/or store. Use to detect a rising or "
            "falling trend."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "category": {
                    "type": "string",
                    "description": "Optional category_id filter (e.g. paint, garden).",
                },
                "store_id": {
                    "type": "string",
                    "description": "Optional store_id filter (e.g. seattle, spokane).",
                },
            },
        },
    },
    {
        "name": "top_products",
        "type": "function",
        "description": (
            "Rank products by total revenue, units, or margin. ascending=true "
            "surfaces underperformers (markdown/clearance candidates)."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "metric": {
                    "type": "string",
                    "description": "Ranking metric: revenue_usd, units, or margin_usd.",
                },
                "limit": {
                    "type": "integer",
                    "description": "How many products (1-50). Default 10.",
                },
                "ascending": {
                    "type": "boolean",
                    "description": "Set true to return the WORST performers.",
                },
                "category": {
                    "type": "string",
                    "description": "Optional category_id filter (e.g. paint, garden).",
                },
            },
        },
    },
    {
        "name": "sales_for_product",
        "type": "function",
        "description": (
            "Total revenue/units/margin for one product plus its per-region "
            "split, or null if not found."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "product_id": {
                    "type": "string",
                    "description": "Zava product id (ZV-<CAT>-NNN), e.g. ZV-PNT-001.",
                }
            },
            "required": ["product_id"],
        },
    },
    {
        "name": "get_order",
        "type": "function",
        "description": "Fetch a single order line by id (ZV-SO-YYYY-NNNNNN), or null if not found.",
        "parameters": {
            "type": "object",
            "properties": {
                "order_id": {
                    "type": "string",
                    "description": "Sales order-line id, e.g. ZV-SO-2026-000001.",
                }
            },
            "required": ["order_id"],
        },
    },
]

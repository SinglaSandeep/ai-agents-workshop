---
title: '3. Test the agent'
layout: default
nav_order: 3
parent: 'Exercise 04: Products Agent (MCP)'
---

# Task 04.03 — Test the Products Agent

## Recommended test cases

| Question | Expected tool call | Expected answer hallmark |
| -------- | ------------------ | ------------------------ |
| "What categories of products do we sell?" | `list_categories` | Returns the 6 categories from the seed |
| "List all beverages under 200 calories." | `list_products(category='Beverages')` then filter | Mentions `PEP-002 Diet Pepsi` (0 cal) and excludes `PEP-003 Mountain Dew` (290 cal) |
| "Tell me about product PEP-006." | `get_product('PEP-006')` | Doritos Nacho Cheese description, $4.99 |
| "What sparkling water do we sell?" | `search_products(text='sparkling')` | Returns `PEP-011 Bubly Sparkling Water - Grapefruit` |
| "What's our PTO policy?" | Should NOT call the catalog | Should respond it cannot help — the orchestrator should route this to HR (Exercise 06) |

## Foundry portal Playground

1. **Agents → pepsico-products-agent → Playground**.
2. Type each of the questions above.
3. Open the **Tool calls** pane and confirm the right tool fires.

## Python smoke test

```powershell
python - <<'PY'
from src.common.foundry_client import get_project_client
from src.common.settings import get_settings

s = get_settings()
openai = get_project_client().get_openai_client()

for q in [
    "What categories of products do we sell?",
    "List all beverages under 200 calories.",
    "Tell me about product PEP-006.",
]:
    print("Q:", q)
    r = openai.responses.create(
        input=q,
        extra_body={"agent_reference": {"name": s.products_agent_name, "type": "agent_reference"}},
    )
    print("A:", r.output_text, "\n---")
PY
```

## Success criteria

{: .success }
> - Each test question fires the expected tool (verifiable in Playground)
> - The Diet Pepsi answer cites `PEP-002`
> - `get_product('PEP-006')` returns Doritos Nacho Cheese

## Next

[Exercise 05 — Create the Marketing Agent (Foundry + MCP + Bing)](../05_marketing_foundry_agent/05_marketing_foundry_agent.md).

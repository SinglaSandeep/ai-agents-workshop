---
title: '3. Test the agent'
layout: default
nav_order: 3
parent: 'Exercise 05: Marketing Agent (MCP + Bing)'
---

# Task 05.03 — Test the Marketing Agent

The interesting test is **routing**: does the agent pick MCP for internal
questions and Bing for public ones?

## Test matrix

| Question | Expected tool | Why |
| -------- | ------------- | --- |
| "Which Gatorade campaigns target youth athletes?" | MCP — `list_campaigns_by_brand('Gatorade')` | Pepsico-internal data |
| "What's the ROI on CMP-2026-003?" | MCP — `campaign_performance('CMP-2026-003')` | Internal KPI |
| "What are the most-discussed Doritos ads in the news this week?" | **Bing** | Public + recency |
| "Who won the 'Crash the Super Bowl' contest in 2026?" | **Bing** | Recency, public info |
| "Summarise our active campaigns and the latest soda-category trends." | **Both** — MCP first, then Bing | Mixed |

## Foundry portal Playground

1. **Agents → pepsico-marketing-agent → Playground**.
2. Run each question and inspect the **Tool calls** pane.
3. Confirm that web answers include **URL citations** (annotations of type
   `url_citation`).

## Streaming Python test (shows citations)

```powershell
python - <<'PY'
from src.common.foundry_client import get_project_client
from src.common.settings import get_settings

openai = get_project_client().get_openai_client()
s = get_settings()

stream = openai.responses.create(
    stream=True,
    input="What are the most-discussed Doritos ads in the news this week?",
    extra_body={"agent_reference": {"name": s.marketing_agent_name, "type": "agent_reference"}},
)

for event in stream:
    if event.type == "response.output_text.delta":
        print(event.delta, end="", flush=True)
    elif event.type == "response.output_item.done" and getattr(event.item, "type", "") == "message":
        for a in (event.item.content[-1].annotations or []):
            if getattr(a, "type", "") == "url_citation":
                print(f"\n[cite] {a.url}")
PY
```

## Success criteria

{: .success }
> - Internal questions show a `pepsico-marketing` MCP tool call
> - Public-news questions show a `web_search` tool call with URL citations
> - The mixed question shows **both** tools fired

## Next

[Exercise 06 — Build the Magentic Orchestrator](../06_orchestrator_agent_framework/06_orchestrator_agent_framework.md).

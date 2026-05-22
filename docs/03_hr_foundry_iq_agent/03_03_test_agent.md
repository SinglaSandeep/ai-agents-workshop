---
title: '3. Test the agent'
layout: default
nav_order: 3
parent: 'Exercise 03: HR Agent (Foundry IQ)'
---

# Task 03.03 — Test the HR Agent

## Option A — Foundry portal Playground

1. Open the Foundry portal → **Agents → pepsico-hr-agent → Playground**.
2. Ask: **"What is the PTO carryover policy at Pepsico?"**.
3. Confirm:
   - The agent calls `knowledge_base_retrieve` (visible in the **Tool calls** pane).
   - The answer mentions the 5-day carryover cap.
   - The final reply ends with `Sources: pepsico_pto_policy.md`.

## Option B — Python smoke test

```powershell
python - <<'PY'
from src.common.foundry_client import get_project_client
from src.common.settings import get_settings

s = get_settings()
project = get_project_client()
openai = project.get_openai_client()

resp = openai.responses.create(
    input="What is the PTO carryover policy at Pepsico?",
    extra_body={"agent_reference": {"name": s.hr_agent_name, "type": "agent_reference"}},
)
print(resp.output_text)
PY
```

You should see a grounded answer with the sources line.

## Test cases

| Question | Expected behaviour |
| -------- | ------------------ |
| "What is the PTO carryover policy?" | Cites `pepsico_pto_policy.md`, mentions 5-day cap |
| "How many days of paid parental leave do primary caregivers get?" | Cites `pepsico_benefits_summary.md`, returns 12 weeks |
| "Can I work from Spain for two months?" | Cites `pepsico_remote_work.md`, refers to Global Mobility Handbook |
| "What is the price of a Doritos bag?" | Returns the "could not find" fallback — this question belongs to the Products agent |

That last test case is the **point**: by constraining the HR agent to its
knowledge base, you guarantee it will not hallucinate outside its domain.
The orchestrator (Exercise 06) is what stops the wrong agent being called in
the first place.

## Success criteria

{: .success }
> - The PTO question returns a grounded answer with the source filename
> - The Products question triggers the "could not find" fallback rather than
>   a made-up price

## Next

[Exercise 04 — Create the Products Agent (Foundry + MCP)](../04_products_foundry_agent/04_products_foundry_agent.md).

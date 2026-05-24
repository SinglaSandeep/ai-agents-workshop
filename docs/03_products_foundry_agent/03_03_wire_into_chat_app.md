---
title: '3. Talk to the agent in DevUI'
layout: default
nav_order: 3
parent: 'Exercise 03: Products Foundry Agent'
---

# Task 03.03 — Talk to the Products Agent in DevUI

## Introduction

In tasks 03.01 and 03.02 you registered the MCP connection and created the
Products Foundry Prompt Agent. The DevUI launcher from Exercise 01 already
references this agent by name (`settings.products_agent_name`), so there is
**no extra wiring** to do — just restart DevUI and the new agent shows up.

This replaces the old "wire into chat app" task — DevUI is the chat app,
and `src/app/devui_launch.py` is the only entrypoint.

## Success Criteria

* DevUI lists `products` as a working entity (no "agent not found" error).
* In the browser, asking the Products agent grounded questions returns
  answers that cite real product ids.
* The same questions return the same answers when called via the OpenAI
  Responses API.

## Key Tasks

### 01: Restart DevUI

If DevUI was already running, stop it (Ctrl+C) and restart so it picks up
the newly created Foundry agent:

```powershell
python -m src.app.devui_launch
```

You should still see all three specs registered. Only `products` will
actually respond — `marketing` and `hr` come online in Exercises 05 and 06.

### 02: Test in the browser

Open <http://127.0.0.1:8080>, pick **products** in the left rail, and try
prompts like:

* *"What flavors of Lay's chips do you carry?"*
* *"Tell me about PEP-007."*
* *"Which beverages are under $5?"*

You should see grounded answers that include real product ids and prices
from Cosmos. In **developer mode**, the right-hand panel shows every MCP
tool call the agent made.

### 03: Test via the Responses API

In a second terminal, prove the same agent works headlessly:

```powershell
curl -X POST http://127.0.0.1:8080/v1/responses `
  -H "Content-Type: application/json" `
  -d '{ "metadata": { "entity_id": "products" }, "input": "What is PEP-007?" }'
```

Or with the OpenAI SDK:

```python
from openai import OpenAI
client = OpenAI(base_url="http://127.0.0.1:8080/v1", api_key="not-needed")
resp = client.responses.create(
    metadata={"entity_id": "products"},
    input="Which colas do you carry?",
)
print(resp.output[0].content[0].text)
```

The Responses API is the contract the Foundry-hosted Marketing agent
(Exercise 05) speaks natively, so any client code you write here will
transfer cleanly to the cloud-hosted version.

<details markdown="block">
<summary><strong>Expand this section if the agent answers from memory instead of calling the tool</strong></summary>

* Re-read the `INSTRUCTIONS` block in `create_products_agent.py`. It must
  say *"Only answer using data returned by the tools"*. If you altered it,
  re-run the script to push a new agent version.
* In the Foundry portal → Agents → your agent → **Playground**, test the
  same prompt. If you see *"Tool call required"* errors, the MCP
  connection's managed identity does not have `Invoker` rights on the
  Container App.

</details>

## Next

Continue to [Exercise 04 — Build & Deploy the Marketing MCP Server](../04_marketing_mcp_server/04_marketing_mcp_server.md).

---
title: '2. Understand the DevUI launcher'
layout: default
nav_order: 2
parent: 'Exercise 01: Scaffold the Chat App'
---

# Task 01.02 — Understand the DevUI Launcher

## Introduction

In the previous task you started DevUI with `python -m src.app.devui_launch`.
There is **no `AGENT_MODE` switch** in this workshop — every specialist
agent is registered as a separate DevUI entity, and you pick which one to
talk to from the left rail (or by passing `entity_id` to the Responses
API). This matches the directory-based discovery pattern shown in the
Azure-Samples `foundry-hosted-agentframework-demos` repo.

| Entity in DevUI | Foundry agent name (`settings`) | First created in |
| --------------- | ------------------------------- | ---------------- |
| `products`      | `settings.products_agent_name`  | Exercise 03 |
| `marketing`     | `settings.marketing_agent_name` | Exercise 05 — Foundry-**hosted** (`ResponsesHostServer`) |
| `hr`            | `settings.store_ops_agent_name`        | Exercise 06 |

{: .important }
> **Hosted vs. Foundry-Prompt-Agent.** The Marketing entity points to a
> *hosted* agent — a container packaged with
> `agent_framework_foundry_hosting.ResponsesHostServer` and deployed to the
> Foundry Agent Service (Exercise 05). The Products and HR entities point to
> *Foundry Prompt Agents* — declarative agents defined via
> `azure-ai-projects` (Exercises 03 and 06). DevUI calls all three through
> the same `FoundryAgent(agent_name=...)` shim, so they look identical from
> the client side.

## Success Criteria

* You can open [src/app/devui_launch.py](https://github.com/SinglaSandeep/ai-agents-workshop/blob/main/src/app/devui_launch.py)
  and explain what each section does.
* You understand why we use `register_cleanup(...)` instead of
  `async with DefaultAzureCredential() as cred:`.

## Key Tasks

### 01: Read `devui_launch.py`

Open [src/app/devui_launch.py](https://github.com/SinglaSandeep/ai-agents-workshop/blob/main/src/app/devui_launch.py)
and walk through:

* The `specs` list — one tuple per specialist agent. The first element is
  the DevUI **entity id** (used as `metadata.entity_id` over the
  Responses API); the second is the **Foundry agent name** loaded from
  `settings`.
* `_build_agent(...)` — constructs a `FoundryAgent` *without* `async with`.
  Per the DevUI README, you must not wrap agents in a context manager —
  DevUI manages the lifetime itself and `async with` would close the
  underlying connection before the first request.
* `register_cleanup(entities[0], credential.close)` — DevUI calls this on
  shutdown so the shared `DefaultAzureCredential` is closed cleanly.
* `serve(entities=..., auth_enabled=False)` — disables bearer-token auth
  because we bind to `127.0.0.1` only. If you change `DEVUI_HOST` to a
  LAN address, set a token via `DEVUI_AUTH_TOKEN` first.

### 02: Optional — invoke via the OpenAI SDK

Leave DevUI running and try the OpenAI Python SDK against it:

```python
from openai import OpenAI
client = OpenAI(base_url="http://127.0.0.1:8080/v1", api_key="not-needed")
resp = client.responses.create(
    metadata={"entity_id": "hr"},          # any of "products" / "marketing" / "hr"
    input="What is the PTO policy?",
)
print(resp.output[0].content[0].text)
```

When you reach Exercise 09 (evaluations) you'll reuse this exact shape — the
evaluator points an OpenAI client at the agent and scores the responses.

## Next

Continue to [Exercise 02 — Build & Deploy the Products MCP Server](../02_products_mcp_server/02_products_mcp_server.md).

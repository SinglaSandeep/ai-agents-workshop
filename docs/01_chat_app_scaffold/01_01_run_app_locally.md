---
title: '1. Run DevUI locally'
layout: default
nav_order: 1
parent: 'Exercise 01: Scaffold the Chat App'
---

# Task 01.01 — Run Agent Framework DevUI Locally

## Introduction

This workshop uses the [Microsoft Agent Framework **DevUI**](https://github.com/microsoft/agent-framework/tree/main/python/packages/devui)
as its frontend — **no custom HTML / FastAPI app**. DevUI is a sample debug UI
shipped by the framework team that:

* auto-generates a chat surface for any registered `Agent` (or workflow)
* exposes an **OpenAI-compatible Responses API** at `/v1/responses`, so the
  same agents are callable from any OpenAI SDK or `curl`
* loads OpenTelemetry traces when enabled

The launcher lives at [src/app/devui_launch.py](https://github.com/SinglaSandeep/ai-agents-workshop/blob/main/src/app/devui_launch.py).
It registers the three Zava specialist agents (`products`, `marketing`,
`hr`) by their Foundry-hosted names — exactly the pattern used in the
reference sample at
<https://github.com/Azure-Samples/foundry-hosted-agentframework-demos>.

{: .note }
> The agents themselves don't exist yet in Foundry — that's what Exercises
> 03, 05, and 06 create. DevUI will still launch in Exercise 01, but
> clicking into an agent before its exercise is complete will return an
> error from the Foundry data plane. That is expected.

## Success Criteria

* `python -m src.app.devui_launch` starts DevUI on port 8080 with no errors.
* You can browse to <http://127.0.0.1:8080> and see the DevUI chat surface.
* The left rail lists the three agents — `products`, `marketing`, `hr`.

## Key Tasks

### 01: Start DevUI

In a terminal, from the `ai-agents-workshop` folder, activate your virtual
environment and launch DevUI:

<details markdown="block">
<summary><strong>Expand this section to view the solution</strong></summary>

```powershell
.\.venv\Scripts\Activate.ps1
python -m src.app.devui_launch
```

On macOS / Linux:

```bash
source .venv/bin/activate
python -m src.app.devui_launch
```

You should see logs ending with:

```
INFO zava.devui: Registered products -> Foundry agent 'zava-products-agent'
INFO zava.devui: Registered marketing -> Foundry agent 'zava-marketing-agent'
INFO zava.devui: Registered hr -> Foundry agent 'zava-store-ops-agent'
INFO zava.devui: Launching DevUI on http://127.0.0.1:8080 with 3 agents
```

A browser tab opens automatically at <http://127.0.0.1:8080>.

</details>

{: .tip }
> Override the port via an environment variable before launching:
>
> ```powershell
> $env:DEVUI_PORT = "8090"
> python -m src.app.devui_launch
> ```
>
> Telemetry to Application Insights is **off** by default and is enabled
> later in [Exercise 11 — Observability](../11_observability/11_observability.md).

### 02: Explore the UI

* Pick an agent from the left rail. Until its exercise is complete you will
  get an "agent not found" error from Foundry — that is fine.
* The **Settings** panel lets you switch between developer mode (raw tool
  call traces) and user mode (clean chat-only view).

### 03: Test the Responses API

DevUI doubles as an OpenAI-compatible server. From a second terminal:

```powershell
curl -X POST http://127.0.0.1:8080/v1/responses `
  -H "Content-Type: application/json" `
  -d '{ "metadata": { "entity_id": "products" }, "input": "hello" }'
```

You can also use the OpenAI Python SDK directly:

```python
from openai import OpenAI
client = OpenAI(base_url="http://127.0.0.1:8080/v1", api_key="not-needed")
resp = client.responses.create(
    metadata={"entity_id": "products"},
    input="What Pepsi colas do you have?",
)
print(resp.output[0].content[0].text)
```

This is the **same** Responses API shape the deployed Foundry-hosted
Marketing agent exposes (Exercise 05), so any client code you write here
will continue to work against the cloud deployment.

Leave the DevUI server running — every subsequent exercise re-uses the same
browser tab for testing.

## Next

Continue to [01.02 — Understand the DevUI launcher](01_02_understand_agent_mode.md).

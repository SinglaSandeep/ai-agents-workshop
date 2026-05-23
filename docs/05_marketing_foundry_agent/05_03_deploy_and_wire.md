---
title: '3. Deploy & wire into chat'
layout: default
nav_order: 3
parent: 'Exercise 05: Marketing Hosted Agent (Foundry IQ + Web Tool)'
---

# Task 05.03 — Run Locally, Deploy to Foundry, Wire Into the Chat UI

## Introduction

The Azure Developer CLI ships an `azd ai` extension that knows how to
package an `agent.yaml` into a hosted-agent image, deploy it to your Foundry
project, and stream its logs.

## Success Criteria

* `azd ai agent run` boots the agent locally on
  `http://localhost:8088/responses`.
* `azd ai agent invoke --local "..."` answers questions over the local
  endpoint.
* `azd ai agent up` returns successfully and `azd ai agent show` lists the
  agent as `Healthy`.
* The chat UI with `AGENT_MODE=marketing` reaches the **hosted** agent and
  answers Pepsico campaign + live-web questions.

## Key Tasks

### 01: Install the azd AI extension (one-time)

```powershell
azd extension install ai
azd ai --help
```

### 02: Run the agent locally

```powershell
cd src/foundry_agents/marketing_hosted
azd ai agent run
```

In another terminal:

```powershell
azd ai agent invoke --local "What is the ROI of CMP-2026-001?"
azd ai agent invoke --local "Any recent news on Gatorade's 2026 campaigns?"
```

### 03: Deploy to Foundry

```powershell
azd ai agent up
azd ai agent show
azd ai agent monitor -f   # live logs
```

`azd ai agent up` builds the Docker image, pushes it to your Foundry-managed
ACR, and creates/updates the hosted agent. The hosted endpoint is registered
back into your Foundry project under the agent name in `agent.yaml`
(`pepsico-marketing-agent`).

### 04: Verify in Foundry portal

Foundry portal → **Agents → pepsico-marketing-agent**. Use the built-in
Playground to test the same prompts. You should see traces under the
**Observability** tab.

### 05: Wire into the chat UI

The orchestrator (Exercise 07) and the simple per-mode dispatcher both look up
the agent by name. Because we kept `MARKETING_AGENT_NAME=pepsico-marketing-agent`,
no chat-app code change is needed — flip the mode:

```
AGENT_MODE=marketing
```

Restart uvicorn and test in the browser:

| Prompt | Expected behaviour |
| ------ | ------------------ |
| *"What active Gatorade campaigns target youth athletes?"* | Calls the **Marketing MCP** tool. |
| *"Summarise the 2025 SuperBowl post-mortem."* | Calls the **Marketing KB** (`knowledge_base_retrieve`). |
| *"Any news on Pepsi's most recent SuperBowl spot?"* | Calls Foundry Toolbox **web_search**; cites URLs. |

The plan pill below each answer should read `marketing`.

## Next

Continue to [Exercise 06 — Create the HR Foundry IQ Agent](../06_hr_foundry_iq_agent/06_hr_foundry_iq_agent.md).

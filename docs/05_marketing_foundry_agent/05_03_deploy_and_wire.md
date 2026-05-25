---
title: '3. Register, run, wire into chat'
layout: default
nav_order: 3
parent: 'Exercise 05: Marketing Prompt Agent (Foundry IQ + Code Interpreter)'
---

# Task 05.03 — Register the Agent and Talk to It

## Introduction

Registering a Foundry Prompt Agent is one Python command. After that, the
chat app, DevUI, and orchestrator all pick it up by name
(`MARKETING_AGENT_NAME`, default `zava-marketing-agent`).

## Success Criteria

* `python -m src.foundry_agents.create_marketing_agent` succeeds.
* The agent shows up in the Foundry portal under **Agents**.
* DevUI talks to the agent under the **marketing** entity.

## Key Tasks

### 01: Register / update the agent

```powershell
python -m src.foundry_agents.create_marketing_agent
```

This calls `project.agents.create_version(...)` on your Foundry project
with the model, instructions, and tool list. It is **idempotent** — re-run
it any time you tweak instructions, tools, or the model.

### 02: Quick sanity check

`run_single_agent` lets you fire a one-shot turn at any of the registered
agents from the terminal:

```powershell
python -m src.foundry_agents.run_single_agent marketing `
  "What active Gatorade campaigns target youth athletes?"
```

You should see the tool calls in the trace and a grounded answer with a
trailing `Tools used: ...` line.

### 03: Verify in Foundry portal

Foundry portal → **Agents → zava-marketing-agent**. Use the built-in
Playground to test the same prompts. The **Tools** tab should list the
Marketing MCP, Code Interpreter, and the Marketing KB MCP.

### 04: Talk to it in DevUI

The DevUI launcher and the orchestrator both look up the agent by name, so
no launcher-code change is needed:

```powershell
python -m src.app.devui_launch
```

Select the **marketing** entity in the sidebar and try:

| Prompt | Expected behaviour |
| ------ | ------------------ |
| *"What active Gatorade campaigns target youth athletes?"* | Calls the **Marketing MCP** tool. |
| *"Summarise the 2025 SuperBowl post-mortem."* | Calls the **Marketing KB** (`knowledge_base_retrieve`). |
| *"Add up the budgets of the active 2026 campaigns."* | Calls the MCP, then **Code Interpreter** to total. |
| *"What's the latest news on Pepsi's SuperBowl spot?"* | Politely declines (no web tool) and offers KB/MCP. |

The plan pill below each answer should read `marketing`.

## Next

Continue to [Exercise 06 — Create the Store-Ops Foundry IQ Agent](../06_store_ops_foundry_iq_agent/06_store_ops_foundry_iq_agent.md).

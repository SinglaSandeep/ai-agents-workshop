---
title: '2. Create the Products Prompt Agent'
layout: default
nav_order: 2
parent: 'Exercise 03: Products Foundry Agent'
---

# Task 03.02 — Create the Products Foundry Prompt Agent

## Introduction

A **Foundry Prompt Agent** is a server-side, versioned bundle of:

* a model deployment name (e.g. `gpt-4.1-mini`),
* an `instructions` system prompt,
* a list of `tools`.

You will write a small script that creates (or updates) a new agent version
named `zava-products-agent`, attaching the MCP connection from the previous
task.

## Success Criteria

* `python -m src.foundry_agents.create_products_agent` runs cleanly.
* The log line `Created agent 'zava-products-agent' version '<id>'` appears.
* The agent shows up in the Foundry portal under **Agents** with a single
  `MCPTool`.

## Key Tasks

### 01: Open the starter script

Open [src/foundry_agents/create_products_agent.py](https://github.com/SinglaSandeep/ai-agents-workshop/blob/main/src/foundry_agents/create_products_agent.py).
The `INSTRUCTIONS` block is already filled in. You just need to implement
`main()` — read its TODO comments.

### 02: Implement `main()`


### 03: Run it

```powershell
python -m src.foundry_agents.create_products_agent
```

Expected log lines:

```
INFO Upserting Foundry project connection zava-products-mcp-conn
INFO Creating agent version: zava-products-agent (model=gpt-4.1-mini, tools=1)
INFO Created agent 'zava-products-agent' version '1'
```

### 04: Verify in the portal

Open the Foundry portal → your project → **Agents → zava-products-agent**.
Confirm:

* Latest version has one tool of type **MCP**.
* Connection name in the tool matches `PRODUCTS_MCP_CONNECTION_NAME`.

## Next

Continue to [03.03 — Wire the agent into the chat UI](03_03_wire_into_chat_app.md).

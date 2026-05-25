---
title: '2. Create the Store-Ops Prompt Agent'
layout: default
nav_order: 2
parent: 'Exercise 06: Store-Ops Foundry IQ Agent'
---

# Task 06.02 — Create the Store-Ops Foundry Prompt Agent

## Introduction

The HR agent has a single MCP tool — the `knowledge_base_retrieve` operation
exposed by the Foundry IQ knowledge base you created in the previous task.
By limiting `allowed_tools` you make sure the model cannot call any other
admin operations on the Search service.

## Success Criteria

* `python -m src.foundry_agents.create_store_ops_agent` succeeds.
* The new agent has one MCP tool, with `allowed_tools=["knowledge_base_retrieve"]`.

## Key Tasks

### 01: Implement `main()`

Open [src/foundry_agents/create_store_ops_agent.py](https://github.com/SinglaSandeep/ai-agents-workshop/blob/main/src/foundry_agents/create_store_ops_agent.py).


### 02: Run it

```powershell
python -m src.foundry_agents.create_store_ops_agent
```

## Next

Continue to [06.03 — Wire the agent into the chat UI](06_03_wire_into_chat_app.md).

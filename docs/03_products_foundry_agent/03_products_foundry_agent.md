---
title: 'Exercise 03: Products Foundry Agent'
layout: default
nav_order: 5
has_children: true
---

# Exercise 03 — Create the Products Foundry Agent (and wire it into the chat UI)

## Scenario

You have a deployed MCP server (Exercise 02) and a runnable chat UI (Exercise
01). It is time to put real intelligence behind the chat. You will create a
**Foundry Prompt Agent** that uses the Products MCP server as a tool, and
wire the FastAPI chat endpoint to call it.

By the end of this exercise users can ask the chat UI things like *"What
Pepsi products do you have?"* or *"Tell me about PEP-001"* and get answers
grounded in the live Cosmos data.

## Description

You will:

1. Register a **Foundry project connection** that points at the Products MCP
   container app you deployed in Exercise 02.
2. Create a Foundry Prompt Agent with focused instructions and the Products
   `MCPTool` attached.
3. Implement a small `run_single_agent("products", query)` helper.
4. Talk to the agent in the **Agent Framework DevUI** (`python -m
   src.app.devui_launch`).

## Architecture

```mermaid
flowchart LR
    U[User browser] --> D[DevUI / Responses API]
    D --> A[Products Foundry Prompt Agent]
    A -->|MCPTool / HTTP| S[Products MCP Server (Container App)]
    S --> C[(Cosmos DB · products)]
```

## Success Criteria

{: .success }
> - A Foundry connection named `pepsico-products-mcp-conn` exists on your
>   project and points at `PRODUCTS_MCP_URL`.
> - A Foundry agent named `pepsico-products-agent` exists with one tool
>   (`MCPTool` → that connection).
> - `python -m src.foundry_agents.create_products_agent` runs without error
>   and prints the new agent version.
> - In DevUI, asking the **products** agent *"What sizes does Pepsi Cola
>   come in?"* returns an answer that cites `PEP-001`.

## Learning Resources

* [Foundry Prompt Agents](https://learn.microsoft.com/azure/ai-foundry/agents/concepts/prompt-agents)
* [`MCPTool` reference](https://learn.microsoft.com/azure/ai-foundry/agents/tools/mcp-tool)
* [Microsoft Agent Framework — Azure AI Agent client](https://learn.microsoft.com/azure/ai-foundry/agents/microsoft-agent-framework)

## Tasks

| Task | Description |
| ---- | ----------- |
| [03.01 — Register the MCP project connection](03_01_register_mcp_connection.md) | Add a connection on the Foundry project that authenticates as the project's managed identity. |
| [03.02 — Create the Products Prompt Agent](03_02_create_products_agent.md) | Implement `create_products_agent.py` and run it. |
| [03.03 — Talk to the agent in DevUI](03_03_wire_into_chat_app.md) | Implement `run_single_agent("products", …)` and chat with the agent in DevUI. |

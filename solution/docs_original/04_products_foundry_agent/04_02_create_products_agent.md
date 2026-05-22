---
title: '2. Create the Products Foundry agent'
layout: default
nav_order: 2
parent: 'Exercise 04: Products Agent (MCP)'
---

# Task 04.02 — Create the Products Foundry Prompt Agent

## The key snippet

```python
products_tool = MCPTool(
    server_label="pepsico-products",
    server_url=settings.products_mcp_url,
    require_approval="never",
    project_connection_id=settings.products_mcp_connection_name,
)

project.agents.create_version(
    agent_name=settings.products_agent_name,
    definition=PromptAgentDefinition(
        model=settings.azure_ai_model_deployment,
        instructions=INSTRUCTIONS,
        tools=[products_tool],
    ),
    description="Pepsico Products specialist (MCP-backed by Cosmos DB).",
)
```

The instructions force the agent to:
- Pick the most specific tool for each question.
- Never invent SKUs, prices, or sizes.
- Always cite the `id` of any product mentioned.

## Steps

1. **Run the script**

   ```powershell
   python -m src.foundry_agents.create_products_agent
   ```

   Expected:

   ```text
   INFO Upserting Foundry project connection pepsico-products-mcp-conn
   INFO Creating agent version: pepsico-products-agent (model=gpt-4.1-mini, tools=1)
   INFO Created agent 'pepsico-products-agent' version '1'
   ```

2. **Verify in the Foundry portal**

   **Agents → pepsico-products-agent** should show:
   - The model deployment
   - The instructions
   - The **pepsico-products** MCP tool, with the four tools (`list_categories`,
     `list_products`, `get_product`, `search_products`) auto-discovered.

## Success criteria

{: .success }
> - The script reports `Created agent 'pepsico-products-agent' version '<n>'`
> - The Foundry portal shows the agent with the 4 underlying tools detected

## Next

[04.03 — Test the agent](04_03_test_agent.md).

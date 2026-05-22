---
title: '2. Create the Marketing Foundry agent'
layout: default
nav_order: 2
parent: 'Exercise 05: Marketing Agent (MCP + Bing)'
---

# Task 05.02 — Create the Marketing Foundry Prompt Agent

## The key snippet

```python
marketing_tool = MCPTool(
    server_label="pepsico-marketing",
    server_url=settings.marketing_mcp_url,
    require_approval="never",
    project_connection_id=settings.marketing_mcp_connection_name,
)

# Grounding with Bing Search — the connection name is wired through the project,
# not as a per-tool argument. The agent runtime resolves the default Bing
# connection on the project.
web_search_tool = WebSearchTool()

project.agents.create_version(
    agent_name=settings.marketing_agent_name,
    definition=PromptAgentDefinition(
        model=settings.azure_ai_model_deployment,
        instructions=INSTRUCTIONS,
        tools=[marketing_tool, web_search_tool],
    ),
)
```

The **instructions** are the contract:

> Use the MCP server for **anything about Pepsico's own campaigns**. Use
> Bing for **anything about competitors, public news, or post-cutoff facts**.
> Never invent Pepsico campaign data.

## Steps

1. **Run the script**

   ```powershell
   python -m src.foundry_agents.create_marketing_agent
   ```

2. **Verify in the Foundry portal**

   **Agents → pepsico-marketing-agent** → confirm both tools are attached:
   - `pepsico-marketing` (MCP, 5 sub-tools)
   - `web_search` (Bing Grounding)

## Success criteria

{: .success }
> - The script reports `Created agent 'pepsico-marketing-agent' version '<n>'`
> - The agent has **both** tools in the Foundry portal

## Next

[05.03 — Test the agent (internal + web)](05_03_test_agent.md).

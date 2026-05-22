---
title: '2. Create the HR Foundry agent'
layout: default
nav_order: 2
parent: 'Exercise 03: HR Agent (Foundry IQ)'
---

# Task 03.02 — Create the HR Foundry Prompt Agent

`src/foundry_agents/create_hr_agent.py` calls
`project_client.agents.create_version(...)` with:

- the model deployment from `.env`
- an `MCPTool` that points at the Foundry IQ KB endpoint
- instructions that force the agent to ground every answer in the KB

## The key snippet

```python
mcp_endpoint = (
    f"{settings.azure_search_endpoint}/knowledgebases/"
    f"{settings.hr_kb_name}/mcp?api-version=2025-11-01-preview"
)

hr_kb_tool = MCPTool(
    server_label="hr-knowledge-base",
    server_url=mcp_endpoint,
    require_approval="never",                       # no human-in-the-loop
    allowed_tools=["knowledge_base_retrieve"],      # only expose retrieval
    project_connection_id=settings.hr_kb_connection_name,
)

agent = project.agents.create_version(
    agent_name=settings.hr_agent_name,
    definition=PromptAgentDefinition(
        model=settings.azure_ai_model_deployment,
        instructions=INSTRUCTIONS,
        tools=[hr_kb_tool],
    ),
    description="Pepsico HR specialist grounded by Foundry IQ.",
)
```

## Steps

1. **Run the script**

   ```powershell
   python -m src.foundry_agents.create_hr_agent
   ```

   Expected output:

   ```text
   INFO Creating agent version: pepsico-hr-agent (model=gpt-4.1-mini, tools=1)
   INFO Created agent 'pepsico-hr-agent' version '1'
   ```

2. **Verify in the Foundry portal**

   - **Agents → pepsico-hr-agent** → you should see the new version, the
     model, the instructions, and the attached `hr-knowledge-base` MCP tool.

## Re-running the script

Each invocation creates a **new version** of the agent. The agent name stays
stable so consumers (the orchestrator) always resolve the latest version.

## Success criteria

{: .success }
> - The script reports `Created agent 'pepsico-hr-agent' version '<n>'`
> - The agent appears in the Foundry portal with the MCP tool attached

## Next

[03.03 — Test the agent](03_03_test_agent.md).

---
title: 'Exercise 06: HR Foundry IQ Agent'
layout: default
nav_order: 8
has_children: true
---

# Exercise 06 — Create the HR Foundry IQ Agent (and wire it into the chat UI)

## Scenario

The Products and Marketing agents pull from Cosmos. HR data, on the other
hand, lives in policy documents. That is exactly what **Foundry IQ** is for:
it indexes the documents in Azure AI Search and exposes a managed
`knowledge_base_retrieve` MCP tool the agent can call.

## Description

You will:

1. Upload Pepsico HR Markdown to an Azure AI Search index, wrap it in a
   Foundry IQ knowledge base, and register a project connection — all via
   one Python script.
2. Create the `pepsico-hr-agent` Prompt Agent that calls the KB.
3. Flip `AGENT_MODE=hr` and ask HR questions in the chat UI.

## Success Criteria

{: .success }
> - Azure AI Search has an index `pepsico-hr-source` with the seed HR docs.
> - A Foundry IQ knowledge base `pepsico-hr-kb` exists.
> - A Foundry project connection `pepsico-hr-kb-conn` points at the KB's MCP
>   endpoint.
> - Foundry agent `pepsico-hr-agent` has one tool: `MCPTool` with
>   `allowed_tools=["knowledge_base_retrieve"]`.
> - With `AGENT_MODE=hr`, asking *"What is the PTO policy?"* returns an
>   answer that ends with a `Sources:` line referencing a real seed file.

## Learning Resources

* [Foundry IQ Knowledge Bases](https://learn.microsoft.com/azure/ai-foundry/iq/overview)
* [Azure AI Search — Knowledge bases preview](https://learn.microsoft.com/azure/search/search-knowledge-base-overview)

## Tasks

| Task | Description |
| ---- | ----------- |
| [06.01 — Create the HR knowledge base](06_01_create_knowledge_base.md) | Implement `setup_hr_knowledge_base.py`. |
| [06.02 — Create the HR Prompt Agent](06_02_create_hr_agent.md) | Implement `create_hr_agent.py`. |
| [06.03 — Wire the agent into the chat UI](06_03_wire_into_chat_app.md) | Flip `AGENT_MODE=hr` and test in the browser. |

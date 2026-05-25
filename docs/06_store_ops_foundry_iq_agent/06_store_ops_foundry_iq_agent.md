---
title: 'Exercise 06: Store-Ops Foundry IQ Agent'
layout: default
nav_order: 8
has_children: true
---

# Exercise 06 — Create the Store-Ops Foundry IQ Agent (and wire it into the chat UI)

## Scenario

The Products and Marketing agents pull from Cosmos. HR data, on the other
hand, lives in policy documents. That is exactly what **Foundry IQ** is for:
it indexes the documents in Azure AI Search and exposes a managed
`knowledge_base_retrieve` MCP tool the agent can call.

## Description

You will:

1. Upload Zava store-ops Markdown to an Azure AI Search index, wrap it in a
   Foundry IQ knowledge base, and register a project connection — all via
   one Python script.
2. Create the `zava-store-ops-agent` Prompt Agent that calls the KB.
3. Talk to the Store Ops agent in DevUI.

## Success Criteria

{: .success }
> - Azure AI Search has an index `zava-store-ops-source` with the seed store-ops docs.
> - A Foundry IQ knowledge base `zava-store-ops-kb` exists.
> - A Foundry project connection `zava-store-ops-kb-conn` points at the KB's MCP
>   endpoint.
> - Foundry agent `zava-store-ops-agent` has one tool: `MCPTool` with
>   `allowed_tools=["knowledge_base_retrieve"]`.
> - In DevUI, the **store_ops** agent answers *"What is the PTO policy?"* with a
>   reply that ends with a `Sources:` line referencing a real seed file.

## Learning Resources

* [Foundry IQ Knowledge Bases](https://learn.microsoft.com/azure/ai-foundry/iq/overview)
* [Azure AI Search — Knowledge bases preview](https://learn.microsoft.com/azure/search/search-knowledge-base-overview)

## Tasks

| Task | Description |
| ---- | ----------- |
| [06.01 — Create the Store-Ops knowledge base](06_01_create_knowledge_base.md) | Implement `setup_store_ops_knowledge_base.py`. |
| [06.02 — Create the Store-Ops Prompt Agent](06_02_create_store_ops_agent.md) | Implement `create_store_ops_agent.py`. |
| [06.03 — Talk to the Store Ops agent in DevUI](06_03_wire_into_chat_app.md) | Restart `devui_launch` and ask store-ops questions. |

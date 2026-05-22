---
title: 'Exercise 05: Marketing Foundry Agent (+ Bing)'
layout: default
nav_order: 7
has_children: true
---

# Exercise 05 — Create the Marketing Foundry Agent (and wire it into the chat UI)

## Scenario

The Marketing team wants the assistant to answer with grounded campaign data
**and** to be able to pull in live web context (industry news, competitor
announcements). That means giving the Marketing agent two tools:

1. The Marketing MCP server (Cosmos truth).
2. Grounding-with-Bing-Search (live web).

## Description

You will:

1. Register a Foundry connection for the Marketing MCP and confirm an
   existing Bing Grounding connection.
2. Create the `pepsico-marketing-agent` Prompt Agent with both tools.
3. Flip `AGENT_MODE=marketing` and chat.

## Success Criteria

{: .success }
> - Foundry connection `pepsico-marketing-mcp-conn` exists on your project.
> - A `Grounding with Bing Search` connection named per
>   `BING_GROUNDING_CONNECTION_NAME` exists on your project.
> - Foundry agent `pepsico-marketing-agent` has **two** tools.
> - With `AGENT_MODE=marketing`, the chat UI answers questions like *"What is
>   the ROI of campaign CMP-2026-001?"* using MCP data, and *"Any news on
>   Pepsi's most recent SuperBowl spot?"* using Bing.

## Learning Resources

* [Grounding with Bing Search in Foundry](https://learn.microsoft.com/azure/ai-foundry/agents/tools/bing-grounding)
* [`WebSearchTool` reference](https://learn.microsoft.com/azure/ai-foundry/agents/tools/web-search)

## Tasks

| Task | Description |
| ---- | ----------- |
| [05.01 — Register the Marketing MCP and Bing connections](05_01_register_mcp_and_bing.md) | One Foundry connection per tool. |
| [05.02 — Create the Marketing Prompt Agent](05_02_create_marketing_agent.md) | Implement `create_marketing_agent.py`. |
| [05.03 — Wire the agent into the chat UI](05_03_wire_into_chat_app.md) | Flip `AGENT_MODE=marketing` and test in the browser. |

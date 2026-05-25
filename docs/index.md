---
title: Contents
layout: default
nav_order: 1
has_children: false
---

# Workshop Contents

| #  | Exercise |
| -- | -------- |
| 00 | [Setup & Verify Pre-Provisioned Resources](00_setup/00_setup.md) |
| 01 | [Scaffold the Chat App (UI, runnable end-to-end)](01_chat_app_scaffold/01_chat_app_scaffold.md) |
| 02 | [Build & Deploy the Products MCP Server](02_products_mcp_server/02_products_mcp_server.md) |
| 03 | [Create the Products Foundry Agent & wire it into the chat](03_products_foundry_agent/03_products_foundry_agent.md) |
| 04 | [Build & Deploy the Marketing MCP Server](04_marketing_mcp_server/04_marketing_mcp_server.md) |
| 05 | [Build the Marketing Prompt Agent (Foundry IQ + Code Interpreter)](05_marketing_foundry_agent/05_marketing_foundry_agent.md) |
| 06 | [Create the Store-Ops Foundry IQ Agent & wire it in](06_store_ops_foundry_iq_agent/06_store_ops_foundry_iq_agent.md) |
| 07 | [Build the Magentic Orchestrator (multi-agent)](07_orchestrator_agent_framework/07_orchestrator_agent_framework.md) |
| 08 | [Add the Response Generator agent](08_response_generator/08_response_generator.md) |
| 09 | [Quality Evaluations on the Marketing Agent](09_evaluations/09_evaluations.md) |
| 10 | [Guardrails & Red Teaming](10_guardrails_red_teaming/10_guardrails_red_teaming.md) |
| 11 | [End-to-End Observability](11_observability/11_observability.md) |
| 12 | [Resource Cleanup](12_cleanup/12_cleanup.md) |


## Test-as-you-go

The FastAPI chat UI is runnable from **Exercise 01** with a hard-coded stub
response. Every subsequent exercise wires another real agent into the same UI
so you can keep testing in the browser as you go.

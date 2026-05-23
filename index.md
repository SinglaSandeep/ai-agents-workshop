---
title: Introduction
layout: home
nav_order: 1
---

# Pepsico AI Agents Workshop (L300)

Welcome! In this workshop you will build an **end-to-end multi-agent Pepsico
business assistant** on Azure using **Microsoft Foundry**, **Microsoft Agent
Framework**, **Foundry IQ**, **Foundry Toolbox** (web search +
code-interpreter), **Model Context Protocol (MCP)** servers on **Azure
Container Apps**, **Azure Cosmos DB**, and the **Foundry hosted-agents**
runtime. The final modules add **quality evaluations**, **guardrails**,
**red teaming**, and **end-to-end observability**.

## What You Will Build

By the end of the workshop you will have:

- Two **MCP servers** (Products and Marketing) backed by **Cosmos DB**,
  deployed to **Azure Container Apps**.
- An **HR specialist agent** in **Microsoft Foundry**, grounded with a
  **Foundry IQ** knowledge base over Pepsico HR policies.
- A **Products specialist agent** (Foundry Prompt Agent) that uses the
  Products MCP server as a tool.
- A **Marketing specialist agent** built on the **Microsoft Agent Framework**
  and **hosted on Microsoft Foundry** (`azd ai agent up`), using the
  **Foundry Toolbox** (web search + code interpreter) and a **Foundry IQ**
  knowledge base of marketing briefs in addition to the Marketing MCP.
- A **Magentic orchestrator** that plans across the three specialists.
- A **Response Generator** that produces the final answer.
- **Quality evaluations** (one-shot, scheduled, continuous) on the hosted
  Marketing agent.
- **Guardrails** (content-filter middleware + custom shared policies) and an
  automated **red-team scan** against the local hosted agent.
- **End-to-end observability** via OpenTelemetry → Application Insights and
  Foundry traces.

## Exercises

| #  | Exercise |
| -- | -------- |
| 00 | [Setup & Verify Pre-Provisioned Resources](docs/00_setup/00_setup.md) |
| 01 | [Scaffold the Chat App](docs/01_chat_app_scaffold/01_chat_app_scaffold.md) |
| 02 | [Build & Deploy the Products MCP Server](docs/02_products_mcp_server/02_products_mcp_server.md) |
| 03 | [Create the Products Foundry Agent](docs/03_products_foundry_agent/03_products_foundry_agent.md) |
| 04 | [Build & Deploy the Marketing MCP Server](docs/04_marketing_mcp_server/04_marketing_mcp_server.md) |
| 05 | [Build the **Foundry-hosted** Marketing Agent (Foundry IQ + Web Tool)](docs/05_marketing_foundry_agent/05_marketing_foundry_agent.md) |
| 06 | [Create the HR Foundry IQ Agent](docs/06_hr_foundry_iq_agent/06_hr_foundry_iq_agent.md) |
| 07 | [Build the Magentic Orchestrator](docs/07_orchestrator_agent_framework/07_orchestrator_agent_framework.md) |
| 08 | [Add the Response Generator Agent](docs/08_response_generator/08_response_generator.md) |
| 09 | [Quality Evaluations on the Hosted Marketing Agent](docs/09_evaluations/09_evaluations.md) |
| 10 | [Guardrails & Red Teaming](docs/10_guardrails_red_teaming/10_guardrails_red_teaming.md) |
| 11 | [End-to-End Observability](docs/11_observability/11_observability.md) |
| 12 | [Resource Cleanup](docs/12_cleanup/12_cleanup.md) |

## Audience & Prerequisites

This is a **300-level** workshop. You should be comfortable with:

- Python 3.11+ and `pip` / virtual environments
- Basic Azure concepts (resource groups, RBAC, managed identity)
- Reading REST and OpenAPI specs
- Using the Azure portal and the `az` CLI

You do **not** need prior experience with the Microsoft Agent Framework,
Foundry hosted agents, Foundry IQ, or MCP — you will learn each as you go.

## Start Here

Begin with [Exercise 00 — Setup](docs/00_setup/00_setup.md).

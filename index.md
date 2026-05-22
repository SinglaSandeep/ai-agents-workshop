---
title: Introduction
layout: home
nav_order: 1
---

# Pepsico AI Agents Workshop (L300)

Welcome! In this workshop you will build an **end-to-end multi-agent Pepsico business assistant** on Azure using **Microsoft Foundry**, **Microsoft Agent Framework**, **Foundry IQ**, **Bing Grounding**, **Model Context Protocol (MCP)** servers on **Azure Container Apps**, and **Azure Cosmos DB**.

## What You Will Build

By the end of the workshop you will have:

- Two **MCP servers** (Products and Marketing) backed by **Cosmos DB**, deployed to **Azure Container Apps**.
- An **HR specialist agent** in **Microsoft Foundry**, grounded with a **Foundry IQ** knowledge base over Pepsico HR policies.
- A **Products specialist agent** (Foundry Prompt Agent) that uses the Products MCP server as a tool.
- A **Marketing specialist agent** (Foundry Prompt Agent) that uses the Marketing MCP server **and** **Bing Grounding** for live web context.
- A **Magentic orchestrator** built with the **Microsoft Agent Framework** that routes and plans across the three specialists.
- A **Response Generator** Foundry Prompt Agent that synthesizes the final answer.
- A **FastAPI chat application** with a CLI, instrumented with OpenTelemetry → Application Insights / Foundry.

## Exercises

| #  | Exercise |
| -- | -------- |
| 00 | [Setup & Verify Pre-Provisioned Resources](docs/00_setup/00_setup.md) |
| 01 | [Build & Deploy the Products MCP Server](docs/01_products_mcp_server/01_products_mcp_server.md) |
| 02 | [Build & Deploy the Marketing MCP Server](docs/02_marketing_mcp_server/02_marketing_mcp_server.md) |
| 03 | [Create the HR Agent with Foundry IQ](docs/03_hr_foundry_iq_agent/03_hr_foundry_iq_agent.md) |
| 04 | [Create the Products Agent (Foundry + MCP)](docs/04_products_foundry_agent/04_products_foundry_agent.md) |
| 05 | [Create the Marketing Agent (Foundry + MCP + Bing)](docs/05_marketing_foundry_agent/05_marketing_foundry_agent.md) |
| 06 | [Build the Magentic Orchestrator](docs/06_orchestrator_agent_framework/06_orchestrator_agent_framework.md) |
| 07 | [Add the Response Generator Agent](docs/07_response_generator_agent/07_response_generator_agent.md) |
| 08 | [Wire the Chat App & Add Observability](docs/08_chat_app_and_observability/08_chat_app_and_observability.md) |
| 09 | [Resource Cleanup](docs/09_cleanup/09_cleanup.md) |

## Audience & Prerequisites

This is a **300-level** workshop. You should be comfortable with:

- Python 3.11+ and `pip` / virtual environments
- Basic Azure concepts (resource groups, RBAC, managed identity)
- Reading REST and OpenAPI specs
- Using the Azure portal and the `az` CLI

You do **not** need prior experience with the Microsoft Agent Framework, Foundry IQ, or MCP — you will learn each as you go.

## Start Here

Begin with [Exercise 00 — Setup](docs/00_setup/00_setup.md).

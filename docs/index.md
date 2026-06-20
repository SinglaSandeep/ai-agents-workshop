---
title: Contents
layout: default
nav_order: 1
has_children: false
---

# Build & Govern AI Agents

Build a multi-agent **"Insights → Action"** assistant for
**Zava**: from a single agent to a governed, orchestrated team deployed to the
cloud. New here? See the [Introduction](../index.md) for the full business +
technology overview.

> **Key idea:** **MCP = tools / actions** · **Foundry IQ = grounding / knowledge.**

The workshop is organised into **7 modules** (plus Setup), each adding one
capability of the assistant; the chat app is runnable end-to-end from Setup.
See the full picture in [Reference Architecture](architecture.md).

## The agents you will build

| Agent | Tools | Role |
| ----- | ----- | ---- |
| **Sales** | `zava-sales` MCP (Cosmos) | Revenue / units / margin trends |
| **Inventory** | `zava-inventory` MCP (Cosmos) | Stock health across distributors & warehouses |
| **Marketing** | `zava-marketing` MCP + Foundry IQ KB | Campaign status, KPIs, ROI |
| **Intent Detector** | none | Classifies a turn as GENERAL vs BUSINESS |
| **Action Recommender** | Code Interpreter | Turns insights into prioritised actions (runs last) |
| **Response Generator** | none | Writes the final user-facing reply |

The **Magentic orchestrator** (Agent Framework) coordinates the
Sales, Inventory, Marketing and Action agents; the Intent Detector and
Response Generator wrap the flow.

---

## Modules at a glance

Use the navigation on the left for every exercise. The path from start to
finish:

| Module | Goal |
| ------ | ---- |
| **Setup** | Verify the pre-provisioned resources and run the chat app end-to-end. |
| **1 · Build Your First Agent** | Learn the agent lifecycle with the **Intent Detector** (no tools yet). |
| **2 · Build the MCP Tools** | Build and Inspector-test the Sales, Inventory & Marketing **MCP servers**. |
| **3 · Give Agents Access to Tools** | Wire the **Sales** and **Inventory** agents to their MCP tools. |
| **4 · Add Knowledge with Foundry IQ** | Build the **Marketing** agent — MCP tools *plus* Foundry IQ knowledge. |
| **5 · Orchestrate & Deploy** | Coordinate the specialists with the **Magentic** pattern, add the Action & Response agents, and deploy. |
| **6 · Evaluate, Trace & Guardrails** | Measure quality, trace behaviour, and add guardrails & red teaming. |
| **7 · Governance & Wrap-Up** | Govern the system, then clean up the resources. |

---

## Test-as-you-go

The FastAPI chat UI runs locally from **Setup (Exercise 01)**. As you
create each specialist agent it becomes available to the Magentic
orchestrator, so you can keep testing the whole assistant in the browser
with `uvicorn src.app.main:app --port 8000`.

---
title: Introduction
layout: home
nav_order: 1
---

# AI Agents Workshop

Welcome. You will build a multi-agent assistant for **Zava**
— a fictional Pacific-Northwest DIY retailer (7 stores + online). Two aspects
to keep in mind as you go: the **business problem** and the **technology**
used to solve it.

---

## 1. The Business Problem

Zava already has the data — sales, inventory, marketing — in separate systems.
**The gap is the join**, so promotional decisions are made late, by hand,
after the weekend's revenue is already lost. The recurring demo throughout the
workshop:

> *"Sales for our Spring Paint Sale in Seattle look soft — which products are
> low on stock, what did last year teach us, and what should the store manager
> do right now?"*

| Domain | Insight it contributes |
| ------ | ---------------------- |
| **Sales** | Paint revenue at Seattle is trending down. |
| **Inventory** | The hero paint SKU is critically low on stock. |
| **Marketing** | A 20%-off promo is live; last year's post-mortem warned this stockout would recur. |

➡️ **Result:** one sourced recommendation — restock amount, new reorder
threshold, and the manager's discount authority — every claim backed by data.

---

## 2. The Technology

You build the solution on a modern, open agent stack:

| Technology | Role in the solution |
| ---------- | -------------------- |
| **Foundry** | Hosts the models and the specialist agents. |
| **Agent Framework** | Orchestrates the agents (the **Magentic** pattern). |
| **Model Context Protocol (MCP)** | Standard tool interface — one MCP server per data domain. |
| **Cosmos DB** | Stores the Sales, Inventory, and Marketing data. |
| **Foundry IQ** | Grounds the Marketing agent in briefs and post-mortems (knowledge). |
| **Code Interpreter** | Lets the Action agent compute prioritised recommendations. |
| **Container Apps** | Hosts the MCP servers and the chat app. |
| **Evaluations · Observability · Guardrails · Red teaming** | Make the assistant trustworthy — measured, observable, and safe. |

> **Key idea:** **MCP = tools / actions** · **Foundry IQ = grounding / knowledge.**

---

## The Goal — a working multi-agent app

By the end you will have built a **complete multi-agent assistant** that shows
how the pieces of a multi-agent app fit together:

- **Multi-agent** — specialist agents coordinated by an orchestrator.
- **Grounded** — answers cite real data and knowledge; the agents never guess.
- **Measured** — quality evaluations and end-to-end observability.
- **Governed** — guardrails and red teaming before it reaches users.
- **Deployed** — running on a hosted endpoint, with clean teardown.

---

## How You Will Build It

You build the assistant incrementally across **7 modules** (plus Setup) — each
module adds one capability, and the chat app is runnable end-to-end from the
start.

| Module | You build | What it adds |
| ------ | --------- | ------------ |
| **Setup & Prerequisites** | Environment + runnable chat app | A verified, repeatable foundation |
| **1 · Build Your First Agent** | Intent Detector agent | The agent lifecycle |
| **2 · Build the MCP Tools** | Sales, Inventory, Marketing MCP servers + Inspector | A reusable tools/actions layer |
| **3 · Give Agents Access to Tools** | Sales & Inventory agents wired to MCP | Grounded specialist agents |
| **4 · Add Knowledge with Foundry IQ** | Marketing agent (MCP + Foundry IQ) | A knowledge-grounded agent |
| **5 · Orchestrate & Deploy** | Magentic orchestrator + Action & Response agents + deploy | Reliable coordination, shipped |
| **6 · Evaluate, Trace & Guardrails** | Evaluations + observability + guardrails | Measured, safe behaviour |
| **7 · Governance & Wrap-Up** | Governance review + cleanup | Governance and teardown |

Work through the modules in order, using the navigation on the left.

## Prerequisites

This is a **purely hands-on lab**. You do **not** need prior experience with
Foundry, the Agent Framework, Foundry IQ, MCP, Azure
Container Apps, Cosmos DB, or any of the evaluation / red-teaming /
observability tooling — every concept is introduced as you
need it and every step shows the full working code inline.

What you do need on your laptop before you start:

- **Python 3.11 or newer** with the ability to create a virtual environment
  (`python -m venv`).
- **Git** to clone the repository.
- **Visual Studio Code** (recommended) or any editor you are comfortable with.
- **PowerShell 7+** (Windows) or **bash / zsh** (macOS / Linux) for the
  terminal commands shown throughout the workshop.

- The **Azure CLI** (`az`) installed and signed in (`az login`). Used to
  read configuration from your pre-provisioned resources.
- An **Azure subscription** with the workshop resources already provisioned
  for you by the platform team (Foundry project, Cosmos DB, Azure AI
  Search, Azure Container Apps environment, Application Insights). You will
  verify access to all of them in [Exercise 00 — Setup](docs/00_setup/00_setup.md).
- Network access to `*.azure.com`, `*.openai.azure.com`,
  `*.cognitiveservices.azure.com`, `*.search.windows.net`,
  `*.azurecontainerapps.io`, `pypi.org`, `ghcr.io` and `mcr.microsoft.com`
  (corporate proxies that block these will need an exception).

That is everything. If you can run `python --version` and `az --version`
successfully, you are ready to begin.

## Start Here

Begin with [Exercise 00 — Setup](docs/00_setup/00_setup.md).

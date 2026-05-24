---
title: '1. Seed the Marketing Foundry IQ KB'
layout: default
nav_order: 1
parent: 'Exercise 05: Marketing Hosted Agent (Foundry IQ + Web Tool)'
---

# Task 05.01 — Seed the Marketing Foundry IQ Knowledge Base

## Introduction

The Marketing MCP server (Exercise 04) is great for **structured** campaign
records, but real marketing teams also work from **unstructured** documents:
campaign briefs, creative one-pagers, post-mortems. We will index a small set
of those into **Foundry IQ** so the hosted agent can ground its answers with
the same `knowledge_base_retrieve` MCP tool you already met in Exercise 06.

## Success Criteria

* Azure AI Search index `zava-marketing-source` exists.
* Foundry IQ knowledge base `zava-marketing-kb` exists with that index as
  a source.
* `zava-marketing-kb-conn` project connection exists on your Foundry
  project.

## Key Tasks

### 01: Inspect the sample documents

```text
src/knowledge_seed/marketing/
├── CMP-2026-001_brief.md
├── CMP-2026-002_brief.md
└── post_mortem_2025_superbowl.md
```

(Three small sample briefs ship with the workshop. Add more if you want richer
demos.)

### 02: Run the seeding script

```powershell
python -m src.foundry_agents.setup_marketing_knowledge_base
```

This creates the AI Search index, uploads the documents (chunked + embedded),
creates the `zava-marketing-kb` knowledge base, and registers the project
connection used by the hosted agent.

<details markdown="block">
<summary><strong>Expand to view the solution implementation</strong></summary>

See [solution/foundry_agents/setup_marketing_knowledge_base.py](https://github.com/SinglaSandeep/ai-agents-workshop/blob/main/solution/foundry_agents/setup_marketing_knowledge_base.py).
It mirrors the HR version from Exercise 06 — index → upload → KB → connection.

</details>

### 03: Confirm in the portal

Foundry portal → **Knowledge bases** → confirm `zava-marketing-kb` lists
the marketing source. Open the KB and run a test query like *"What is the
goal of the Gatorade 2026 SuperBowl campaign?"*.

## Next

Continue to [05.02 — Build the hosted Marketing agent](05_02_build_hosted_marketing_agent.md).

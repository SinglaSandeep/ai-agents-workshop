---
title: '1. Create the Store-Ops knowledge base'
layout: default
nav_order: 1
parent: 'Exercise 06: Store-Ops Foundry IQ Agent'
---

# Task 06.01 — Create the Store-Ops Foundry IQ Knowledge Base

## Introduction

`src/knowledge_seed/store_ops/` ships a handful of Zava store-ops policy Markdown files.
You will write a one-shot script that:

1. Uploads each `*.md` into an Azure AI Search **index**.
2. Wraps the index in a Foundry IQ **knowledge base**.
3. Registers a Foundry project **connection** that the agent will use to
   call the KB's MCP endpoint.

Everything is done via the preview REST API of Azure AI Search to match what
the Foundry IQ portal would create.

## Success Criteria

* `python -m src.foundry_agents.setup_store_ops_knowledge_base` runs cleanly and
  prints a JSON summary.
* The Search index `zava-store-ops-source` lists the seed documents.
* The KB endpoint
  `https://<search>.search.windows.net/knowledgebases/zava-store-ops-kb` returns
  HTTP 200 to a GET (via the portal).
* Foundry project connection `zava-store-ops-kb-conn` exists.

## Key Tasks

### 01: Inspect the seed docs

List `src/knowledge_seed/store_ops/`. Each file is a short Markdown policy:

```
employee_onboarding.md
pto_and_scheduling.md
...
```

### 02: Implement `setup_store_ops_knowledge_base.py`

Open [src/foundry_agents/setup_store_ops_knowledge_base.py](https://github.com/SinglaSandeep/ai-agents-workshop/blob/main/src/foundry_agents/setup_store_ops_knowledge_base.py)
and follow the TODOs.


### 03: Run it

```powershell
python -m src.foundry_agents.setup_store_ops_knowledge_base
```

## Next

Continue to [06.02 — Create the Store-Ops Prompt Agent](06_02_create_store_ops_agent.md).

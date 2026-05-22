---
title: '1. Register MCP + Bing connections'
layout: default
nav_order: 1
parent: 'Exercise 05: Marketing Foundry Agent (+ Bing)'
---

# Task 05.01 — Register the Marketing MCP and Bing Connections

## Introduction

Foundry agents reach external systems through **project connections**. The
Marketing agent uses two:

* A `RemoteTool` connection to the Marketing MCP container app
  (`MARKETING_MCP_URL`).
* A `BingGrounding` connection — usually pre-provisioned by the platform team
  because it requires the Bing Search resource to exist.

## Success Criteria

* Connection `pepsico-marketing-mcp-conn` exists on your project.
* A Bing Grounding connection exists; its display name matches
  `BING_GROUNDING_CONNECTION_NAME` in `.env`.

## Key Tasks

### 01: Marketing MCP connection

`create_marketing_agent.py` (next task) handles this for you with the same
`upsert_project_connection` helper you used in Exercise 03.

### 02: Confirm (or create) the Bing connection

In the Foundry portal → **Management center → Connections**, look for a
connection of type **Grounding with Bing Search**. If one exists:

* Copy its display name into `.env` as `BING_GROUNDING_CONNECTION_NAME`.

If one does **not** exist:

<details markdown="block">
<summary><strong>Expand this section to create the Bing connection</strong></summary>

1. In the Azure portal, create a **Grounding with Bing Search** resource in
   the same region as your Foundry project. Note its resource id.
2. In Foundry portal → Management center → Connections → **+ New connection**
   → choose **Grounding with Bing Search** → paste the resource id → name
   the connection (e.g. `pepsico-bing-grounding`) → **Create**.
3. Set `BING_GROUNDING_CONNECTION_NAME=pepsico-bing-grounding` in `.env`.

</details>

## Next

Continue to [05.02 — Create the Marketing Prompt Agent](05_02_create_marketing_agent.md).

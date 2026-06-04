---
title: '3. Run the server locally'
layout: default
nav_order: 3
parent: 'Exercise 02: Products MCP Server'
---

# Task 02.03 — Run the Products MCP Server Locally

## Introduction

Before you containerise the server you want to know it works against your real
Cosmos data. You will start it locally on port 8001 and then call it from the
MCP Inspector, which is a small browser-based JSON-RPC client bundled with
the MCP SDK.

## Success Criteria

* `uvicorn src.mcp_servers.products.server:app --port 8001` prints
  `Application startup complete.`
* The MCP Inspector at <http://localhost:6274> lists the four tools.
* `list_categories` returns the categories seeded in Task 02.01.

## Key Tasks

### 01: Start the server

```powershell
uvicorn src.mcp_servers.products.server:app --port 8001
```

You should see uvicorn start on port 8001 and a FastMCP banner log a line per
registered tool.

### 02: Launch the MCP Inspector

In a second terminal:

```powershell
npx @modelcontextprotocol/inspector
```

The Inspector opens at <http://localhost:6274>. Configure it:

* **Transport**: `Streamable HTTP`
* **URL**: `http://127.0.0.1:8001/mcp`

Click **Connect**.

### 03: Call each tool

In the Inspector sidebar you should see the four tools. Click each in turn:

| Tool | Args | Expected |
| ---- | ---- | -------- |
| `list_categories` | _none_ | `["paint", "power-tools", ...]` |
| `list_products` | `{ "category": "paint" }` | array of 4-5 product dicts |
| `get_product` | `{ "product_id": "ZV-PNT-001" }` | The Premium Interior Paint record |
| `search_products` | `{ "text": "white" }` | products mentioning "white" |


## Next

Continue to [02.04 — Deploy to Azure Container Apps](02_04_deploy_container_app.md).

---
title: 'Exercise 02: Products MCP Server'
layout: default
nav_order: 4
has_children: true
---

# Exercise 02 — Build & Deploy the Products MCP Server

## Scenario

The Products Foundry agent (Exercise 03) needs typed, structured access to the
Zava DIY product catalog stored in Azure Cosmos DB. **Model Context Protocol
(MCP)** gives any compliant LLM client — including Foundry's `MCPTool` — a
strongly-typed JSON-RPC interface to a remote tool server.

In this exercise you will build the first of two MCP servers, run it locally,
and deploy it as a public Azure Container App.

## Description

You will:

1. Seed the Cosmos DB `products` container with 12 sample Zava SKUs.
2. Implement a **FastMCP** server in Python that surfaces four tools on top
   of Cosmos DB.
3. Run the server locally and exercise it with the MCP inspector.
4. Containerise the server and deploy it to **Azure Container Apps**.
5. Record the public URL of the running server in `.env` so Exercise 03 can
   register it as a Foundry connection.

## Architecture

```mermaid
flowchart LR
    A[Foundry Products Agent\n(Exercise 03)] -->|MCPTool / HTTP| S[Products MCP Server\nAzure Container Apps]
    S -->|SDK| C[(Azure Cosmos DB\nzava / products)]
```

## Success Criteria

{: .success }
> By the end of this exercise:
>
> - The Cosmos `zava` database exists with a `products` container holding
>   12 documents.
> - `zava-products-mcp` runs locally on <http://127.0.0.1:8001/mcp> and the
>   MCP inspector lists the four tools.
> - A Container App named `zava-products-mcp` is running in your ACA
>   environment with a public ingress URL.
> - `PRODUCTS_MCP_URL=<...>/mcp` is set in `.env`.
> - `curl <url>/mcp` returns a 405 (the server is reachable; GET is rejected
>   by design — MCP uses POST).

## Learning Resources

* [Introduction to Model Context Protocol](https://learn.microsoft.com/azure/ai-services/agents/model-context-protocol)
* [FastMCP — Python MCP server framework](https://github.com/jlowin/fastmcp)
* [Deploy with `az containerapp up`](https://learn.microsoft.com/azure/container-apps/containerapp-up)

## Tasks

| Task | Description |
| ---- | ----------- |
| [02.01 — Seed Cosmos DB with product data](02_01_seed_cosmos.md) | Create the `products` container and upsert 12 documents. |
| [02.02 — Build the FastMCP server](02_02_build_mcp_server.md) | Implement `cosmos_repo.py` and `server.py`. |
| [02.03 — Run the server locally](02_03_run_locally.md) | Start the server and test it with the MCP inspector. |
| [02.04 — Deploy to Azure Container Apps](02_04_deploy_container_app.md) | Build the image, push to ACR, run `az containerapp up`. |

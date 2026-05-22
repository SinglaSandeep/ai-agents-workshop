---
title: 'Exercise 04: Marketing MCP Server'
layout: default
nav_order: 6
has_children: true
---

# Exercise 04 — Build & Deploy the Marketing MCP Server

## Scenario

The chat app now has one specialist (Products). Time to add a second domain
— **marketing campaigns**. The Marketing Foundry agent (Exercise 05) needs
structured access to live campaign data: who runs them, on which channels,
with what KPIs. You will build a second FastMCP server, very similar in shape
to the Products one, and deploy it as a second Container App.

## Description

You will:

1. Seed the Cosmos `marketing_campaigns` container with sample campaigns.
2. Implement a FastMCP server with five tools.
3. Run it locally and verify with the MCP Inspector.
4. Deploy it to Azure Container Apps and record `MARKETING_MCP_URL`.

## Success Criteria

{: .success }
> - The `marketing_campaigns` container holds at least 5 documents.
> - `pepsico-marketing-mcp` runs locally on <http://127.0.0.1:8002/mcp>.
> - A Container App named `pepsico-marketing-mcp` is `Running` with public
>   ingress.
> - `MARKETING_MCP_URL=https://<fqdn>/mcp` is set in `.env`.

## Learning Resources

* [Cosmos DB SQL query reference](https://learn.microsoft.com/azure/cosmos-db/nosql/query/)
* [FastMCP tool decorators](https://github.com/jlowin/fastmcp#tools)

## Tasks

| Task | Description |
| ---- | ----------- |
| [04.01 — Seed Cosmos DB with marketing campaign data](04_01_seed_cosmos.md) | Create the `marketing_campaigns` container and upsert seed data. |
| [04.02 — Build the FastMCP server](04_02_build_mcp_server.md) | Implement `cosmos_repo.py` and `server.py` (five tools). |
| [04.03 — Deploy to Azure Container Apps](04_03_deploy_container_app.md) | Build, push, run `az containerapp up`. |

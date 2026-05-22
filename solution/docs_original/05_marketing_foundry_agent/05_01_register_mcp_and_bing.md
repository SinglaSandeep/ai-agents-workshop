---
title: '1. Register MCP & Bing connections'
layout: default
nav_order: 1
parent: 'Exercise 05: Marketing Agent (MCP + Bing)'
---

# Task 05.01 — Register the Marketing MCP and Bing Grounding Connections

## Part A — Marketing MCP connection

`create_marketing_agent.py` upserts it for you, identical to the Products
flow. If your platform team has already created it, the script becomes a
no-op.

## Part B — Grounding with Bing Search

The **Grounding with Bing Search** tool needs **two** Azure objects:

1. A **Grounding with Bing Search** resource (an Azure-managed Bing tenancy).
2. A **Foundry project connection** of type `ApiKey` or
   `AAD` that points at the resource. (`AAD` is recommended when the resource
   supports it; `ApiKey` is the default.)

Most Pepsico workshop environments will have these pre-provisioned. To
confirm:

```powershell
# 1. Confirm a Grounding-with-Bing-Search resource exists in the RG
az resource list -g $env:AZURE_RESOURCE_GROUP `
  --resource-type Microsoft.Bing/accounts -o table

# 2. List the Foundry project's connections
az rest --method get `
  --url "https://management.azure.com$env:AZURE_AI_PROJECT_RESOURCE_ID/connections?api-version=2025-10-01-preview" `
  --query "value[?properties.category=='GroundingWithBingSearch'].name" -o tsv
```

The printed connection name is what goes in `.env`:

```bash
BING_GROUNDING_CONNECTION_NAME=<that-name>
```

### If the Bing connection does not exist

1. Open Foundry portal → **Management center → Connections → + New connection**.
2. Pick **Grounding with Bing Search**.
3. Select your Bing resource and choose **Project managed identity** auth.
4. Name it `pepsico-bing-grounding` (matching the default in `.env.sample`).

{: .important }
> Bing Grounding is a paid Azure service. Check your cost-management policy
> and `tier` before enabling it on a long-lived workshop environment.

## Success criteria

{: .success }
> - `MARKETING_MCP_URL` and `BING_GROUNDING_CONNECTION_NAME` are set in `.env`
> - Both connections appear under **Management center → Connections** in the
>   Foundry portal

## Next

[05.02 — Create the Marketing Foundry agent](05_02_create_marketing_agent.md).

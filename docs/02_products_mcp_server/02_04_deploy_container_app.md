---
title: '4. (Optional) Deploy to Azure Container Apps'
layout: default
nav_order: 4
parent: 'Exercise 02: Products MCP Server'
---

# Task 02.04 — (Optional) Deploy the Products MCP Server to Azure Container Apps
{: .no_toc }

> .note
> **This module is OPTIONAL.** Exercises 03+ work fine against the **local**
> `http://127.0.0.1:8001/mcp` URL from Task 02.03. Complete this module only
> if you plan to host the MCP server out-of-band and want the Foundry agent
> to reach it over a public HTTPS endpoint. The remaining exercises do not
> depend on the values produced here.

## Introduction

This task walks you through everything required to host the Products MCP
server on Azure Container Apps **from scratch** — creating the Azure
Container Registry (Basic SKU), a Log Analytics workspace, the Container
Apps environment, building the image, deploying the app, and wiring up the
managed identity it uses to read Cosmos DB.

If your environment already has these resources pre-provisioned (e.g. from
Exercise 00), skip the *Provision* steps and jump straight to
[*05: Build the image*](#05-build-and-push-the-image-to-acr).

## Success Criteria

* An ACR (Basic SKU), a Log Analytics workspace, and a Container Apps
  environment exist in the resource group.
* A Container App named `zava-products-mcp` is `Running` on that env.
* External HTTPS ingress is enabled on port 8001.
* The app's system-assigned identity has the **Cosmos DB Built-in Data
  Contributor** role on the Cosmos account.
* `curl -I https://<fqdn>/mcp` returns `HTTP/1.1 405 Method Not Allowed`.
* `PRODUCTS_MCP_URL=https://<fqdn>/mcp` is saved in `.env`.

## Key Tasks

### 01: Inspect the Dockerfile

Open [src/mcp_servers/products/Dockerfile](https://github.com/SinglaSandeep/ai-agents-workshop/blob/main/src/mcp_servers/products/Dockerfile).
Key things to notice:

* Base image is `python:3.12-slim`.
* Only the code the Products server needs is copied in (you do **not** want
  to ship the rest of the workshop into the container).
* The startup command runs `uvicorn` against `src.mcp_servers.products.server:app`.

### 02: Hydrate your shell from `.env`

The `az` CLI reads from the **process environment** (`$env:*`).
PowerShell does **not** auto-load `.env` — the Python app does that via
`python-dotenv`, but `az` does not. Run this once per shell session from
the repo root:

```powershell
Get-Content .env | Where-Object { $_ -and $_ -notmatch '^\s*#' } | ForEach-Object {
    $name, $value = $_ -split '=', 2
    if ($name -and $value) {
        [Environment]::SetEnvironmentVariable($name.Trim(), $value.Trim().Trim('"'), 'Process')
    }
}
```

### 03: Pick names and capture core values

```powershell
# --- pick / confirm these names (must be globally unique where noted) ---
$SUB         = $env:AZURE_SUBSCRIPTION_ID
$RG          = $env:AZURE_RESOURCE_GROUP             # e.g. aifounry-rg
$LOC         = if ($env:ACA_LOCATION) { $env:ACA_LOCATION } else { "eastus2" }
$ACR         = $env:ACR_NAME                         # globally unique, 5-50 lowercase alphanum
$LAW         = "zava-law"                         # Log Analytics workspace name
$ENV         = if ($env:ACA_ENVIRONMENT) { $env:ACA_ENVIRONMENT } else { "zava-aca-env" }
$APP         = "zava-products-mcp"
$COSMOS_ACCT = $env:COSMOS_ACCOUNT                   # e.g. cosmos-ai-2025

az account set --subscription $SUB
$SUB; $RG; $LOC; $ACR; $LAW; $ENV; $APP; $COSMOS_ACCT
```

All eight lines must be non-empty before continuing.

### 04: Provision ACR + Log Analytics + ACA environment

Skip this step if your workshop environment already has these resources.


### 05: Build and push the image to ACR

`az containerapp up --source .` only looks for a Dockerfile at the root of
the source folder. Since ours lives at
`src/mcp_servers/products/Dockerfile`, build the image first with
`az acr build` (which accepts `--file`).

```powershell
az acr build `
  --registry $ACR `
  --image zava-products-mcp:latest `
  --file src/mcp_servers/products/Dockerfile `
  .

$IMG = "$ACR.azurecr.io/zava-products-mcp:latest"
$IMG
```

### 06: Deploy the Container App


### 07: Grant the app pull rights on ACR

If ACR admin is disabled (recommended), give the Container App's
system-assigned identity the **AcrPull** role on the registry so it can
pull the image on cold-start.


### 08: Grant the app Cosmos data-plane access

The Container App needs the **Cosmos DB Built-in Data Contributor** role
on the Cosmos account to query data with `DefaultAzureCredential`.


### 09: Allow the Container App through the Cosmos DB firewall

If the Cosmos account has IP rules enabled (the default for the workshop
account), you must add the Container App's outbound public IP to the
allowlist. Otherwise the first tool call will return a `403 Forbidden`
with an error like *"Request originated from IP ... through public internet.
This is blocked by your Cosmos DB account firewall settings."*


### 10: Smoke-test the public URL

```powershell
$FQDN = az containerapp show -n $APP -g $RG `
  --query properties.configuration.ingress.fqdn -o tsv

curl -I "https://$FQDN/mcp"
```

A `HTTP/1.1 405 Method Not Allowed` is the correct response — MCP expects
POST, not GET. The 405 confirms DNS, TLS, and the container are all
healthy. If you get `502` or `503`, tail the logs:

```powershell
az containerapp logs show -n $APP -g $RG --follow
```

### 11: Save the URL

Add to `.env`:

```
PRODUCTS_MCP_URL=https://<fqdn>/mcp
```

…and re-hydrate the shell (Task 02) so subsequent exercises pick it up.

## Next

Continue to [Exercise 03 — Create the Products Foundry Agent](../03_products_foundry_agent/03_products_foundry_agent.md).

---
title: '4. Deploy to Azure Container Apps'
layout: default
nav_order: 4
parent: 'Exercise 02: Products MCP Server'
---

# Task 02.04 — Deploy the Products MCP Server to Azure Container Apps

## Introduction

The Foundry Products agent (Exercise 03) needs a public URL to reach the MCP
server, so you will containerise the server and run it on the
**pre-provisioned** Azure Container Apps environment.

`az containerapp up` is the simplest path — it builds the image with Buildah,
pushes it to your ACR, and creates / updates the Container App and ingress
in one command.

## Success Criteria

* A Container App named `pepsico-products-mcp` is `Running` in your ACA env.
* The app has external HTTP ingress on port 8001.
* `curl https://<fqdn>/mcp` returns HTTP 405 (POST-only endpoint).
* `PRODUCTS_MCP_URL=https://<fqdn>/mcp` is saved in `.env`.

## Key Tasks

### 01: Inspect the Dockerfile

Open [src/mcp_servers/products/Dockerfile](../../src/mcp_servers/products/Dockerfile).
Key things to notice:

* Base image is `python:3.12-slim`.
* Only the code the Products server needs is copied in (you do **not** want
  to ship the rest of the workshop into the container).
* The startup command runs `uvicorn` against `src.mcp_servers.products.server:app`.

### 02: Confirm your environment variables

You must have these set in your shell (or `.env`) from Exercise 00:

```powershell
$RG  = $env:AZURE_RESOURCE_GROUP
$ACR = $env:ACR_NAME
$ENV = $env:ACA_ENVIRONMENT
$LOC = $env:ACA_LOCATION

$RG; $ACR; $ENV; $LOC
```

### 03: Deploy with `az containerapp up`

<details markdown="block">
<summary><strong>Expand this section to view the solution</strong></summary>

From the repo root:

```powershell
$APP = "pepsico-products-mcp"

az containerapp up `
  --name $APP `
  --resource-group $RG `
  --location $LOC `
  --environment $ENV `
  --registry-server "$ACR.azurecr.io" `
  --source . `
  --target-port 8001 `
  --ingress external `
  --env-vars `
    COSMOS_ENDPOINT=$env:COSMOS_ENDPOINT `
    COSMOS_DATABASE=$env:COSMOS_DATABASE `
    COSMOS_PRODUCTS_CONTAINER=$env:COSMOS_PRODUCTS_CONTAINER `
  --dockerfile src/mcp_servers/products/Dockerfile
```

When the command finishes, copy the FQDN it prints (looks like
`pepsico-products-mcp.<env-hash>.eastus2.azurecontainerapps.io`).

</details>

### 04: Assign managed identity + Cosmos role

The Container App needs a managed identity that has the
**Cosmos DB Built-in Data Contributor** role on the Cosmos account.

<details markdown="block">
<summary><strong>Expand this section to view the solution</strong></summary>

```powershell
$COSMOS_ACCT = "<your-cosmos-account-name>"

# 1. Enable the system-assigned identity.
az containerapp identity assign `
  --name $APP -g $RG --system-assigned

# 2. Grab its principalId.
$PID = az containerapp show -n $APP -g $RG `
  --query identity.principalId -o tsv

# 3. Grant the data-plane role.
az cosmosdb sql role assignment create `
  --account-name $COSMOS_ACCT -g $RG `
  --scope "/" `
  --principal-id $PID `
  --role-definition-id "00000000-0000-0000-0000-000000000002"
```

</details>

### 05: Smoke-test the public URL

```powershell
$FQDN = az containerapp show -n $APP -g $RG --query properties.configuration.ingress.fqdn -o tsv
curl -I "https://$FQDN/mcp"
```

A `HTTP/1.1 405 Method Not Allowed` is the correct response — MCP expects
POST, not GET. The 405 confirms TLS and DNS work.

### 06: Save the URL

Add to `.env`:

```
PRODUCTS_MCP_URL=https://<fqdn>/mcp
```

## Next

Continue to [Exercise 03 — Create the Products Foundry Agent](../03_products_foundry_agent/03_products_foundry_agent.md).

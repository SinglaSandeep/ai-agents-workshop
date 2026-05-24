---
title: '3. (Optional) Deploy to Azure Container Apps'
layout: default
nav_order: 3
parent: 'Exercise 04: Marketing MCP Server'
---

# Task 04.03 — (Optional) Deploy the Marketing MCP Server to Azure Container Apps
{: .no_toc }

> .note
> **This module is OPTIONAL.** Exercises 05+ work fine against the **local**
> `http://127.0.0.1:8002/mcp` URL from Task 04.02. Complete this module only
> if you plan to host the Marketing MCP server out-of-band and want the
> Marketing Foundry agent to reach it over a public HTTPS endpoint.

## Introduction

This task mirrors [Task 02.04 — Deploy the Products MCP Server](../02_products_mcp_server/02_04_deploy_container_app.md)
but for the Marketing server. The only differences are the app name, the
Dockerfile path, the listening port (`8002`), and the Cosmos container
env-var passed in.

If your subscription does **not** yet have an ACR, a Log Analytics
workspace, and a Container Apps environment, complete steps 03–04 of
Task 02.04 first — those resources are shared by both MCP servers and
only need to be created once.

## Success Criteria

* Container App `pepsico-marketing-mcp` is `Running` on the shared ACA env.
* External HTTPS ingress is enabled on port 8002.
* The app's system-assigned identity has **AcrPull** on the registry and
  **Cosmos DB Built-in Data Contributor** on the Cosmos account.
* `curl -I https://<fqdn>/mcp` returns `HTTP/1.1 405 Method Not Allowed`.
* `MARKETING_MCP_URL=https://<fqdn>/mcp` is saved in `.env`.

## Key Tasks

### 01: Inspect the Dockerfile

Open [src/mcp_servers/marketing/Dockerfile](https://github.com/SinglaSandeep/ai-agents-workshop/blob/main/src/mcp_servers/marketing/Dockerfile).
It is identical to the Products Dockerfile except it copies only the
marketing module and launches uvicorn on
`src.mcp_servers.marketing.server:app` listening on `8002`.

### 02: Hydrate your shell from `.env`

```powershell
Get-Content .env | Where-Object { $_ -and $_ -notmatch '^\s*#' } | ForEach-Object {
    $name, $value = $_ -split '=', 2
    if ($name -and $value) {
        [Environment]::SetEnvironmentVariable($name.Trim(), $value.Trim().Trim('"'), 'Process')
    }
}
```

### 03: Confirm the shared infrastructure exists

These should already exist if you completed Task 02.04. Verify:

```powershell
$SUB         = $env:AZURE_SUBSCRIPTION_ID
$RG          = $env:AZURE_RESOURCE_GROUP
$LOC         = if ($env:ACA_LOCATION) { $env:ACA_LOCATION } else { "eastus2" }
$ACR         = $env:ACR_NAME
$ENV         = if ($env:ACA_ENVIRONMENT) { $env:ACA_ENVIRONMENT } else { "pepsico-aca-env" }
$APP         = "pepsico-marketing-mcp"
$COSMOS_ACCT = $env:COSMOS_ACCOUNT

az account set --subscription $SUB

az acr show          -n $ACR -g $RG --query name -o tsv
az containerapp env show -n $ENV -g $RG --query name -o tsv
```

If either of the last two commands errors with `ResourceNotFound`, go back
to [Task 02.04 step 04](../02_products_mcp_server/02_04_deploy_container_app.md#04-provision-acr--log-analytics--aca-environment)
and provision them before continuing.

### 04: Build and push the image to ACR

```powershell
az acr build `
  --registry $ACR `
  --image pepsico-marketing-mcp:latest `
  --file src/mcp_servers/marketing/Dockerfile `
  .

$IMG = "$ACR.azurecr.io/pepsico-marketing-mcp:latest"
$IMG
```

### 05: Deploy the Container App

<details markdown="block">
<summary><strong>Expand this section to view the solution</strong></summary>

```powershell
az containerapp up `
  --name $APP `
  --resource-group $RG `
  --location $LOC `
  --environment $ENV `
  --image $IMG `
  --target-port 8002 `
  --ingress external `
  --env-vars `
    COSMOS_ENDPOINT=$env:COSMOS_ENDPOINT `
    COSMOS_DATABASE=$env:COSMOS_DATABASE `
    COSMOS_MARKETING_CONTAINER=$env:COSMOS_MARKETING_CONTAINER
```

When the command finishes, copy the FQDN it prints (looks like
`pepsico-marketing-mcp.<env-hash>.eastus2.azurecontainerapps.io`).

</details>

### 06: Grant the app pull rights on ACR

<details markdown="block">
<summary><strong>Expand this section to view the solution</strong></summary>

```powershell
az containerapp identity assign `
  --name $APP -g $RG --system-assigned

$APP_PID = az containerapp show -n $APP -g $RG `
  --query identity.principalId -o tsv

$ACR_ID = az acr show -n $ACR -g $RG --query id -o tsv

if (-not $APP_PID -or -not $ACR_ID) {
    throw "APP_PID or ACR_ID is empty. Re-run step 03 to set `$RG, `$ACR, `$APP, then retry."
}
$APP_PID; $ACR_ID

az role assignment create `
  --assignee $APP_PID `
  --role AcrPull `
  --scope "$ACR_ID"

az containerapp registry set `
  --name $APP -g $RG `
  --server "$ACR.azurecr.io" `
  --identity system
```

</details>

### 07: Grant the app Cosmos data-plane access

<details markdown="block">
<summary><strong>Expand this section to view the solution</strong></summary>

```powershell
az cosmosdb sql role assignment create `
  --account-name $COSMOS_ACCT -g $RG `
  --scope "/" `
  --principal-id $APP_PID `
  --role-definition-id "00000000-0000-0000-0000-000000000002"
```

</details>

### 08: Smoke-test the public URL

```powershell
$FQDN = az containerapp show -n $APP -g $RG `
  --query properties.configuration.ingress.fqdn -o tsv

curl -I "https://$FQDN/mcp"
```

Expect `HTTP/1.1 405 Method Not Allowed`. If you get `502` / `503`,
tail the logs:

```powershell
az containerapp logs show -n $APP -g $RG --follow
```

### 09: Save the URL

Add to `.env`:

```
MARKETING_MCP_URL=https://<fqdn>/mcp
```

…and re-hydrate the shell (step 02) so later exercises pick it up.

## Next

Continue to [Exercise 05 — Create the Marketing Foundry Agent](../05_marketing_foundry_agent/05_marketing_foundry_agent.md).

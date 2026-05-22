---
title: '3. Deploy to Azure Container Apps'
layout: default
nav_order: 3
parent: 'Exercise 04: Marketing MCP Server'
---

# Task 04.03 — Deploy the Marketing MCP Server

## Introduction

You will repeat the Container Apps deploy from Task 02.04, this time for the
Marketing server. The only difference is the app name, the Dockerfile path,
the port (`8002`), and the env-var passed for the container name.

## Success Criteria

* Container App `pepsico-marketing-mcp` is `Running` with public ingress.
* `MARKETING_MCP_URL=https://<fqdn>/mcp` is set in `.env`.

## Key Tasks

### 01: Deploy with `az containerapp up`

<details markdown="block">
<summary><strong>Expand this section to view the solution</strong></summary>

```powershell
$APP = "pepsico-marketing-mcp"

az containerapp up `
  --name $APP `
  --resource-group $RG `
  --location $LOC `
  --environment $ENV `
  --registry-server "$ACR.azurecr.io" `
  --source . `
  --target-port 8002 `
  --ingress external `
  --env-vars `
    COSMOS_ENDPOINT=$env:COSMOS_ENDPOINT `
    COSMOS_DATABASE=$env:COSMOS_DATABASE `
    COSMOS_MARKETING_CONTAINER=$env:COSMOS_MARKETING_CONTAINER `
  --dockerfile src/mcp_servers/marketing/Dockerfile
```

</details>

### 02: Assign managed identity + Cosmos role

```powershell
az containerapp identity assign --name $APP -g $RG --system-assigned

$PID = az containerapp show -n $APP -g $RG --query identity.principalId -o tsv
az cosmosdb sql role assignment create `
  --account-name $COSMOS_ACCT -g $RG `
  --scope "/" --principal-id $PID `
  --role-definition-id "00000000-0000-0000-0000-000000000002"
```

### 03: Save the URL

```
MARKETING_MCP_URL=https://<fqdn>/mcp
```

## Next

Continue to [Exercise 05 — Create the Marketing Foundry Agent](../05_marketing_foundry_agent/05_marketing_foundry_agent.md).

---
title: '3. Run locally and deploy to ACA'
layout: default
nav_order: 3
parent: 'Exercise 02: Marketing MCP Server'
---

# Task 02.03 — Run Locally and Deploy to Azure Container Apps

This is the same flow as [01.03](../01_products_mcp_server/01_03_run_locally.md)
and [01.04](../01_products_mcp_server/01_04_deploy_container_app.md), with
the marketing names substituted.

## Run locally

```powershell
pepsico-marketing-mcp
```

In a second terminal:

```powershell
npx -y @modelcontextprotocol/inspector --transport streamable-http http://127.0.0.1:8002/mcp
```

You should see all five tools listed.

## Deploy to ACA

```powershell
$RG  = $env:AZURE_RESOURCE_GROUP
$ACR = $env:ACR_NAME
$ENV = $env:ACA_ENVIRONMENT
$LOC = $env:ACA_LOCATION
$APP = "pepsico-marketing-mcp"
$IMG = "$ACR.azurecr.io/${APP}:v1"

az acr build -r $ACR -t $IMG -f src/mcp_servers/marketing/Dockerfile .

az containerapp up `
  --name $APP `
  --resource-group $RG `
  --environment $ENV `
  --location $LOC `
  --image $IMG `
  --target-port 8002 `
  --ingress external `
  --system-assigned `
  --env-vars `
    COSMOS_ENDPOINT=$env:COSMOS_ENDPOINT `
    COSMOS_DATABASE=$env:COSMOS_DATABASE `
    COSMOS_MARKETING_CONTAINER=$env:COSMOS_MARKETING_CONTAINER
```

Grant the new managed identity Cosmos data access:

```powershell
$miPrincipalId = az containerapp identity show -g $RG -n $APP --query principalId -o tsv
$cosmosAcct    = ($env:COSMOS_ENDPOINT -replace 'https://','' -replace '\.documents\.azure\.com.*','')
az cosmosdb sql role assignment create `
  --account-name $cosmosAcct -g $RG `
  --scope "/" `
  --principal-id $miPrincipalId `
  --role-definition-id "00000000-0000-0000-0000-000000000002"
```

Capture the URL and save it in `.env`:

```powershell
$FQDN = az containerapp show -g $RG -n $APP --query properties.configuration.ingress.fqdn -o tsv
"MARKETING_MCP_URL=https://$FQDN/mcp"
```

Smoke test:

```powershell
curl -i -X POST "https://$FQDN/mcp" `
  -H "Content-Type: application/json" `
  -H "Accept: application/json, text/event-stream" `
  -d '{"jsonrpc":"2.0","id":1,"method":"tools/list"}'
```

## Success criteria

{: .success }
> - `pepsico-marketing-mcp` Container App returns `Running`
> - The smoke test returns HTTP 200 with all five tools
> - `MARKETING_MCP_URL` is set in `.env`

## Next

[Exercise 03 — Create the HR Agent with Foundry IQ](../03_hr_foundry_iq_agent/03_hr_foundry_iq_agent.md).

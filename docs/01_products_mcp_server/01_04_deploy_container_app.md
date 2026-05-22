---
title: '4. Deploy to Azure Container Apps'
layout: default
nav_order: 4
parent: 'Exercise 01: Products MCP Server'
---

# Task 01.04 — Deploy the Products MCP Server to Azure Container Apps

You will:
1. Build the image with the provided `Dockerfile`.
2. Push it to your pre-provisioned Azure Container Registry.
3. Create / update the Container App with a **system-assigned managed identity**.
4. Grant the managed identity `Cosmos DB Built-in Data Contributor` so the
   running container can read from Cosmos passwordlessly.
5. Record the public URL in `.env`.

## Steps

1. **Set the variables you'll reuse**

   ```powershell
   $RG  = $env:AZURE_RESOURCE_GROUP                  # e.g. pepsico-aiworkshop-rg
   $ACR = $env:ACR_NAME                              # e.g. pepsicoworkshopacr
   $ENV = $env:ACA_ENVIRONMENT                       # e.g. pepsico-aca-env
   $LOC = $env:ACA_LOCATION                          # e.g. eastus2
   $APP = "pepsico-products-mcp"
   $IMG = "$ACR.azurecr.io/${APP}:v1"
   ```

2. **Log in to ACR and build the image**

   `az acr build` runs the build remotely in ACR — you don't need a local
   Docker daemon to be powerful.

   ```powershell
   az acr login -n $ACR
   az acr build -r $ACR -t $IMG -f src/mcp_servers/products/Dockerfile .
   ```

3. **Create (or update) the Container App**

   ```powershell
   az containerapp up `
     --name $APP `
     --resource-group $RG `
     --environment $ENV `
     --location $LOC `
     --image $IMG `
     --target-port 8001 `
     --ingress external `
     --system-assigned `
     --env-vars `
       COSMOS_ENDPOINT=$env:COSMOS_ENDPOINT `
       COSMOS_DATABASE=$env:COSMOS_DATABASE `
       COSMOS_PRODUCTS_CONTAINER=$env:COSMOS_PRODUCTS_CONTAINER
   ```

   `az containerapp up` is idempotent — re-running with a new `--image` tag
   simply updates the running revision.

4. **Grant the Container App's managed identity Cosmos access**

   ```powershell
   $miPrincipalId = az containerapp identity show -g $RG -n $APP --query principalId -o tsv
   $cosmosAcct    = ($env:COSMOS_ENDPOINT -replace 'https://','' -replace '\.documents\.azure\.com.*','')

   az cosmosdb sql role assignment create `
     --account-name $cosmosAcct -g $RG `
     --scope "/" `
     --principal-id $miPrincipalId `
     --role-definition-id "00000000-0000-0000-0000-000000000002"
   ```

5. **Grab the public URL and save it in `.env`**

   ```powershell
   $FQDN = az containerapp show -g $RG -n $APP --query properties.configuration.ingress.fqdn -o tsv
   $URL  = "https://$FQDN/mcp"
   Write-Host "PRODUCTS_MCP_URL=$URL"
   ```

   Add the printed line to your `.env` (or overwrite the existing
   `PRODUCTS_MCP_URL=` entry).

6. **Smoke-test the deployed server**

   ```powershell
   curl -i -X POST $URL `
     -H "Content-Type: application/json" `
     -H "Accept: application/json, text/event-stream" `
     -d '{"jsonrpc":"2.0","id":1,"method":"tools/list"}'
   ```

   You should see HTTP 200 and a JSON list of the four tools.

7. **(Optional) Restrict ingress to the Foundry project's egress range**

   Production deployments typically lock down ingress with a VNet integration
   and IP allow-list. Out of scope for the workshop; see
   [Container Apps networking](https://learn.microsoft.com/azure/container-apps/networking).

## Troubleshooting

<details markdown="block"><summary><strong>403 from Cosmos in the container logs</strong></summary>

The managed-identity role assignment can take a few minutes to propagate.
Wait two minutes and try again, or re-run the `az cosmosdb sql role assignment create` command.

</details>

<details markdown="block"><summary><strong>Container fails to start: `KeyError: COSMOS_ENDPOINT`</strong></summary>

You forgot the `--env-vars` flag in step 3. Update with:

```powershell
az containerapp update -g $RG -n $APP `
  --set-env-vars COSMOS_ENDPOINT=$env:COSMOS_ENDPOINT COSMOS_DATABASE=$env:COSMOS_DATABASE COSMOS_PRODUCTS_CONTAINER=$env:COSMOS_PRODUCTS_CONTAINER
```

</details>

## Success criteria

{: .success }
> - `az containerapp show -g $RG -n pepsico-products-mcp --query properties.runningStatus -o tsv` returns `Running`
> - The smoke-test `curl` returns HTTP 200 with the four tools
> - `PRODUCTS_MCP_URL` is set in `.env`

## Next

[Exercise 02 — Build & Deploy the Marketing MCP Server](../02_marketing_mcp_server/02_marketing_mcp_server.md).

---
title: '3. Verify pre-provisioned resources'
layout: default
nav_order: 3
parent: 'Exercise 00: Setup & Verify Resources'
---

# Task 00.03 — Verify Pre-Provisioned Azure Resources

Your platform team should have created the following resources. Find each one
in the portal (or via `az`) and copy its identifier into `.env`.

| `.env` variable | Resource type | How to find it |
| --------------- | ------------- | -------------- |
| `AZURE_SUBSCRIPTION_ID` | Subscription | `az account show --query id -o tsv` |
| `AZURE_TENANT_ID` | Tenant | `az account show --query tenantId -o tsv` |
| `AZURE_RESOURCE_GROUP` | Resource group containing all workshop resources | Portal → Resource groups |
| `AZURE_AI_PROJECT_ENDPOINT` | **Foundry project** endpoint | Portal → Microsoft Foundry → your project → **Overview → Endpoint** |
| `AZURE_AI_PROJECT_NAME` | Foundry project display name | Same blade |
| `AZURE_AI_PROJECT_RESOURCE_ID` | Foundry project ARM id | `az resource show -g <rg> -n <project> --resource-type Microsoft.CognitiveServices/accounts/projects --query id -o tsv` |
| `AZURE_AI_MODEL_DEPLOYMENT` | Model deployment name on the Foundry project | Foundry portal → **Models + endpoints → Deployments** |
| `AZURE_SEARCH_ENDPOINT` | Azure AI Search | `az search service show -g <rg> -n <name> --query "hostName" -o tsv` (prefix with `https://`) |
| `COSMOS_ENDPOINT` | Azure Cosmos DB account | `az cosmosdb show -g <rg> -n <account> --query documentEndpoint -o tsv` |
| `ACA_ENVIRONMENT` | Container Apps environment name | `az containerapp env list -g <rg> --query "[].name" -o tsv` |
| `ACR_NAME` | Azure Container Registry name | `az acr list -g <rg> --query "[].name" -o tsv` |
| `APPLICATIONINSIGHTS_CONNECTION_STRING` | Application Insights | Portal → Application Insights → **Properties → Connection String** |

## Steps

1. **Find your subscription, tenant, and resource group**

   ```powershell
   az account show --query "{sub:id, tenant:tenantId, name:name}" -o json
   az group list --query "[].name" -o tsv
   ```

   Pick the resource group your platform team gave you (typically `zava-aiworkshop-rg`).

2. **Find the Foundry project**

   ```powershell
   $RG = "zava-aiworkshop-rg"
   az resource list -g $RG --resource-type Microsoft.CognitiveServices/accounts/projects -o table
   ```

   Copy the **endpoint URL** (looks like `https://<account>.services.ai.azure.com/api/projects/<project>`) into `AZURE_AI_PROJECT_ENDPOINT`, and the ARM id into `AZURE_AI_PROJECT_RESOURCE_ID`.

3. **List the model deployments on the project**

   ```powershell
   az cognitiveservices account deployment list -g $RG -n <foundry-account> -o table
   ```

   Pick a chat-completions model such as `gpt-4.1-mini` or `gpt-4o` and put the **deployment name** (not the model name) into `AZURE_AI_MODEL_DEPLOYMENT`.

4. **Find Azure AI Search**

   ```powershell
   az search service list -g $RG -o table
   ```

   Set `AZURE_SEARCH_ENDPOINT=https://<name>.search.windows.net`.

5. **Find Cosmos DB**

   ```powershell
   az cosmosdb list -g $RG -o table
   ```

   Set `COSMOS_ENDPOINT=https://<account>.documents.azure.com:443/`. The workshop
   will create the `zava` database and the two containers on first seed run
   (Exercises 01 & 02).

6. **Find the Container Apps environment & ACR**

   ```powershell
   az containerapp env list -g $RG -o table
   az acr list -g $RG -o table
   ```

7. **Confirm the Bing Grounding connection on the Foundry project**

   Open the Foundry portal → **Management center → Connections** and confirm
   a **Grounding with Bing Search** connection exists. Note its display name
   and set `BING_GROUNDING_CONNECTION_NAME` in `.env`.

   If it does not exist, Exercise 05 walks you through creating it.

8. **Confirm your RBAC**

   Your user (or the workshop service principal) must have:

   | Role | Scope |
   | ---- | ----- |
   | `Cosmos DB Built-in Data Contributor` | Cosmos DB account |
   | `Search Service Contributor` + `Search Index Data Contributor` | Azure AI Search service |
   | `Azure AI Developer` | Foundry project |
   | `AcrPush` | Container Registry |
   | `Contributor` | Resource group (for Container Apps create/update) |

   Verify with:

   ```powershell
   az role assignment list --assignee (az ad signed-in-user show --query id -o tsv) -g $RG --query "[].roleDefinitionName" -o tsv
   ```

## Success criteria

{: .success }
> - Every variable in the table above is set in `.env`
> - `az resource list -g $RG -o table` shows: Foundry account + project, Cosmos
>   DB, Azure AI Search, Container Apps environment, ACR, App Insights, and the
>   Bing Grounding connection
> - You have the listed RBAC roles

## Next

Continue to [00.04 — Verify your environment](00_04_verify_environment.md).

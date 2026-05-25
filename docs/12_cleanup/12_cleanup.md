---
title: 'Exercise 12: Resource Cleanup'
layout: default
nav_order: 14
has_children: false
---

# Exercise 12 — Resource Cleanup

## Scenario

The platform-team-provisioned resources (Foundry account, Cosmos DB, AI Search,
ACR, ACA environment, App Insights) are shared and should **not** be deleted.
The artefacts *you* created during the workshop, however, are yours to
remove. This exercise lists them and shows the safe way to delete each one.

## Success Criteria

{: .success }
> - The Products MCP Container App is removed.
> - The Foundry Prompt Agents you created are removed.
> - The Foundry project connections you registered are removed.
> - The Store Ops and Marketing Foundry IQ knowledge bases (and their Search indexes)
>   are removed.
> - The Cosmos `products` and `marketing_campaigns` containers (and optionally
>   the `zava` database) are removed.
> - The evaluation schedules and continuous-eval rule are removed.
> - The local `red_team_output/` and `eval_output/` artefacts are deleted.

## Key Tasks

### 01: Delete the Container Apps you deployed

```powershell
$RG = $env:AZURE_RESOURCE_GROUP
az containerapp delete -g $RG -n zava-products-mcp --yes
az containerapp delete -g $RG -n zava-marketing-mcp --yes
```

### 02: Delete the Foundry Prompt Agents

In the Foundry portal → **Agents**, delete:

* `zava-store-ops-agent`
* `zava-products-agent`
* `zava-marketing-agent`
* `zava-response-generator`

Or via Python:


### 03: Delete the Foundry project connections

In the Foundry portal → **Management center → Connections**, delete:

* `zava-products-mcp-conn`
* `zava-marketing-mcp-conn`
* `zava-store-ops-kb-conn`
* `zava-marketing-kb-conn`

### 04: Delete the Store Ops + Marketing knowledge bases

```powershell
$SEARCH = $env:AZURE_SEARCH_ENDPOINT
$API    = "2025-11-01-preview"
$TOKEN  = az account get-access-token --resource https://search.azure.com/ --query accessToken -o tsv

foreach ($kb in "zava-store-ops-kb","zava-marketing-kb") {
  curl -X DELETE -H "Authorization: Bearer $TOKEN" "$SEARCH/knowledgebases/$kb?api-version=$API"
}
foreach ($idx in "zava-store-ops-source","zava-marketing-source") {
  curl -X DELETE -H "Authorization: Bearer $TOKEN" "$SEARCH/indexes/$idx?api-version=$API"
}
```

### 05: Remove evaluation schedules

Foundry portal → **Observability → Evaluations → Schedules** → delete
`marketing-quality-daily` and `marketing-continuous`. If you created the
Azure Monitor alert, also delete `marketing-quality-low`.

### 06: Delete the Cosmos containers

```powershell
$COSMOS = "<your-cosmos-account-name>"
az cosmosdb sql container delete -a $COSMOS -g $RG -d zava -n products --yes
az cosmosdb sql container delete -a $COSMOS -g $RG -d zava -n marketing_campaigns --yes
# optional: delete the database too
# az cosmosdb sql database delete -a $COSMOS -g $RG -n zava --yes
```

### 07: Local cleanup (optional)

```powershell
Remove-Item -Recurse -Force src\evaluations\eval_output -ErrorAction SilentlyContinue
Remove-Item -Recurse -Force src\red_team\red_team_output -ErrorAction SilentlyContinue
deactivate
Remove-Item -Recurse -Force .venv
Remove-Item .env
```

## You are done

Thanks for completing the Zava AI Agents Workshop.

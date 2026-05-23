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
> - The hosted Marketing agent (`azd ai agent down`) is removed.
> - The Foundry Prompt Agents you created are removed.
> - The Foundry project connections you registered are removed.
> - The HR and Marketing Foundry IQ knowledge bases (and their Search indexes)
>   are removed.
> - The Cosmos `products` and `marketing_campaigns` containers (and optionally
>   the `pepsico` database) are removed.
> - The evaluation schedules and continuous-eval rule are removed.
> - The local `red_team_output/` and `eval_output/` artefacts are deleted.

## Key Tasks

### 01: Tear down the hosted Marketing agent

```powershell
cd src/foundry_agents/marketing_hosted
azd ai agent down
```

### 02: Delete the Products MCP Container App

```powershell
$RG = $env:AZURE_RESOURCE_GROUP
az containerapp delete -g $RG -n pepsico-products-mcp --yes
az containerapp delete -g $RG -n pepsico-marketing-mcp --yes  # if you ever deployed the MCP-only variant
```

### 03: Delete the Foundry Prompt Agents

In the Foundry portal → **Agents**, delete:

* `pepsico-hr-agent`
* `pepsico-products-agent`
* `pepsico-response-generator`

(The `pepsico-marketing-agent` is removed by `azd ai agent down` above.)

Or via REST:

<details markdown="block">
<summary><strong>Expand for CLI / Python deletion</strong></summary>

```python
from src.common.foundry_client import get_project_client
from src.common.settings import get_settings

s = get_settings()
project = get_project_client()
for name in (s.hr_agent_name, s.products_agent_name, s.marketing_agent_name, s.response_agent_name):
    try:
        project.agents.delete(agent_name=name)
        print("deleted", name)
    except Exception as exc:
        print("skip", name, exc)
```

</details>

### 04: Delete the Foundry project connections

In the Foundry portal → **Management center → Connections**, delete:

* `pepsico-products-mcp-conn`
* `pepsico-marketing-mcp-conn`
* `pepsico-hr-kb-conn`
* `pepsico-marketing-kb-conn`

### 05: Delete the HR + Marketing knowledge bases

```powershell
$SEARCH = $env:AZURE_SEARCH_ENDPOINT
$API    = "2025-11-01-preview"
$TOKEN  = az account get-access-token --resource https://search.azure.com/ --query accessToken -o tsv

foreach ($kb in "pepsico-hr-kb","pepsico-marketing-kb") {
  curl -X DELETE -H "Authorization: Bearer $TOKEN" "$SEARCH/knowledgebases/$kb?api-version=$API"
}
foreach ($idx in "pepsico-hr-source","pepsico-marketing-source") {
  curl -X DELETE -H "Authorization: Bearer $TOKEN" "$SEARCH/indexes/$idx?api-version=$API"
}
```

### 06: Remove evaluation schedules

Foundry portal → **Observability → Evaluations → Schedules** → delete
`marketing-quality-daily` and `marketing-continuous`. If you created the
Azure Monitor alert, also delete `marketing-quality-low`.

### 07: Delete the Cosmos containers

```powershell
$COSMOS = "<your-cosmos-account-name>"
az cosmosdb sql container delete -a $COSMOS -g $RG -d pepsico -n products --yes
az cosmosdb sql container delete -a $COSMOS -g $RG -d pepsico -n marketing_campaigns --yes
# optional: delete the database too
# az cosmosdb sql database delete -a $COSMOS -g $RG -n pepsico --yes
```

### 08: Local cleanup (optional)

```powershell
Remove-Item -Recurse -Force solution\evaluations\eval_output -ErrorAction SilentlyContinue
Remove-Item -Recurse -Force solution\red_team\red_team_output -ErrorAction SilentlyContinue
deactivate
Remove-Item -Recurse -Force .venv
Remove-Item .env
```

## You are done

Thanks for completing the Pepsico AI Agents Workshop.

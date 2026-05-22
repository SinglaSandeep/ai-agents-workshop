---
title: 'Exercise 09: Resource Cleanup'
layout: default
nav_order: 11
has_children: false
---

# Exercise 09 — Resource Cleanup

## Scenario

The platform-team-provisioned resources (Foundry account, Cosmos DB, AI Search,
ACR, ACA environment, App Insights, Bing) are shared and should **not** be
deleted. The artefacts *you* created during the workshop, however, are
yours to remove. This exercise lists them and shows the safe way to delete
each one.

## Success Criteria

{: .success }
> - The two Container Apps you deployed are removed.
> - The Foundry agents you created are removed.
> - The Foundry project connections you registered are removed.
> - The HR Foundry IQ knowledge base and Search index are removed.
> - The Cosmos `products` and `marketing_campaigns` containers (and optionally
>   the `pepsico` database) are removed.

## Key Tasks

### 01: Delete the Container Apps

```powershell
$RG = $env:AZURE_RESOURCE_GROUP
az containerapp delete -g $RG -n pepsico-products-mcp --yes
az containerapp delete -g $RG -n pepsico-marketing-mcp --yes
```

### 02: Delete the Foundry agents

In the Foundry portal → **Agents**, delete:

* `pepsico-hr-agent`
* `pepsico-products-agent`
* `pepsico-marketing-agent`
* `pepsico-response-generator`

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

### 03: Delete the Foundry project connections

In the Foundry portal → **Management center → Connections**, delete:

* `pepsico-products-mcp-conn`
* `pepsico-marketing-mcp-conn`
* `pepsico-hr-kb-conn`

(Leave the `Grounding with Bing Search` connection if your platform team
created it for you.)

### 04: Delete the HR knowledge base + index

```powershell
$SEARCH = $env:AZURE_SEARCH_ENDPOINT
$API    = "2025-11-01-preview"
$TOKEN  = az account get-access-token --resource https://search.azure.com/ --query accessToken -o tsv

curl -X DELETE -H "Authorization: Bearer $TOKEN" `
  "$SEARCH/knowledgebases/pepsico-hr-kb?api-version=$API"

curl -X DELETE -H "Authorization: Bearer $TOKEN" `
  "$SEARCH/indexes/pepsico-hr-source?api-version=$API"
```

### 05: Delete the Cosmos containers

```powershell
$COSMOS = "<your-cosmos-account-name>"
az cosmosdb sql container delete -a $COSMOS -g $RG -d pepsico -n products --yes
az cosmosdb sql container delete -a $COSMOS -g $RG -d pepsico -n marketing_campaigns --yes
# optional: delete the database too
# az cosmosdb sql database delete -a $COSMOS -g $RG -n pepsico --yes
```

### 06: Local cleanup (optional)

```powershell
deactivate
Remove-Item -Recurse -Force .venv
Remove-Item .env
```

## You are done

Thanks for completing the Pepsico AI Agents Workshop.

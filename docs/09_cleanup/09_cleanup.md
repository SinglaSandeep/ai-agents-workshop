---
title: 'Exercise 09: Cleanup'
layout: default
nav_order: 11
has_children: false
---

# Exercise 09 — Cleanup Resources You Created

The Foundry account, Cosmos DB, Search service, Container Apps environment,
ACR, and Bing connection were provisioned for you and are typically shared.
You should **not** delete those. However, you should remove the per-attendee
artefacts you created in this workshop.

## What to remove

| Artefact | Created in | How to remove |
| -------- | ---------- | ------------- |
| `pepsico-products-mcp` Container App | Ex. 01 | `az containerapp delete -g $RG -n pepsico-products-mcp -y` |
| `pepsico-marketing-mcp` Container App | Ex. 02 | `az containerapp delete -g $RG -n pepsico-marketing-mcp -y` |
| Cosmos `products` container | Ex. 01 | Data Explorer → right-click → Delete container |
| Cosmos `marketing_campaigns` container | Ex. 02 | Data Explorer → right-click → Delete container |
| `pepsico-hr-source` Search index | Ex. 03 | Portal → Search service → Indexes → Delete |
| `pepsico-hr-kb` Foundry IQ knowledge base | Ex. 03 | Foundry portal → Knowledge bases → Delete |
| `pepsico-hr-kb-conn` Foundry connection | Ex. 03 | Foundry portal → Connections → Delete |
| `pepsico-products-mcp-conn` Foundry connection | Ex. 04 | Foundry portal → Connections → Delete |
| `pepsico-marketing-mcp-conn` Foundry connection | Ex. 05 | Foundry portal → Connections → Delete |
| 4 Foundry agents | Ex. 03-07 | Foundry portal → Agents → Delete each |

{: .warning }
> Do **NOT** delete the Foundry project, the Cosmos DB account, the Search
> service, the Container Apps environment, the ACR, the Application Insights
> instance, or the Bing Grounding resource — these are shared workshop
> resources.

## One-shot teardown script (per-attendee artefacts only)

```powershell
$RG = $env:AZURE_RESOURCE_GROUP

# 1. Container Apps
az containerapp delete -g $RG -n pepsico-products-mcp -y
az containerapp delete -g $RG -n pepsico-marketing-mcp -y

# 2. Cosmos containers
$cosmosAcct = ($env:COSMOS_ENDPOINT -replace 'https://','' -replace '\.documents\.azure\.com.*','')
az cosmosdb sql container delete -g $RG -a $cosmosAcct -d $env:COSMOS_DATABASE -n $env:COSMOS_PRODUCTS_CONTAINER -y
az cosmosdb sql container delete -g $RG -a $cosmosAcct -d $env:COSMOS_DATABASE -n $env:COSMOS_MARKETING_CONTAINER -y

# 3. Search index
$searchName = ($env:AZURE_SEARCH_ENDPOINT -replace 'https://','' -replace '\.search\.windows\.net.*','')
az search index delete -g $RG --service-name $searchName --name $env:HR_KB_SOURCE_ID -y

# 4. Foundry agents (Python helper)
python - <<'PY'
from src.common.foundry_client import get_project_client
from src.common.settings import get_settings
s = get_settings()
client = get_project_client()
for name in (s.hr_agent_name, s.products_agent_name, s.marketing_agent_name, s.response_agent_name):
    try:
        client.agents.delete(agent_name=name)
        print("deleted", name)
    except Exception as e:
        print("skip", name, e)
PY
```

The Foundry IQ knowledge base and the Foundry connections are most reliably
removed in the Foundry portal — do those by hand.

## Success criteria

{: .success }
> - `az containerapp list -g $RG -o tsv --query "[].name"` does not contain
>   either MCP app
> - The two Cosmos containers and the Search index are gone
> - The four Foundry agents are gone from the project
> - The shared resources (Foundry account/project, Cosmos account, Search
>   service, ACA environment, ACR, App Insights, Bing connection) are
>   **still present**

## You are done!

You have built an end-to-end Pepsico multi-agent assistant. From here, ideas
to extend:

- Add a **Sales** specialist with another MCP server (sales orders in SQL DB).
- Replace Magentic with the **Handoff** pattern for a chained content
  workflow (researcher → writer → editor).
- Wire **content safety** filters on the response generator output.
- Add **evaluation** runs in Foundry against a curated test set.

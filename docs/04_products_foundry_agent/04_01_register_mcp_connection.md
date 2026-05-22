---
title: '1. Register the MCP connection'
layout: default
nav_order: 1
parent: 'Exercise 04: Products Agent (MCP)'
---

# Task 04.01 — Register the Products MCP as a Foundry Connection

`create_products_agent.py` does this automatically as its first step, but
it's worth understanding what gets created.

## What is a Foundry project connection?

A **connection** is a named, authenticated handle that an agent can use
when calling an external tool. For an MCP tool, the connection's `target` is
the MCP endpoint, and its `authType` controls how the call is authenticated.
We use **`ProjectManagedIdentity`** so the agent runtime gets a token using
the project's own identity — no API keys to manage.

## What the helper does

`src/common/foundry_client.py::upsert_project_connection` calls the
ARM REST API:

```
PUT https://management.azure.com{AZURE_AI_PROJECT_RESOURCE_ID}
    /connections/pepsico-products-mcp-conn?api-version=2025-10-01-preview
```

with body:

```json
{
  "name": "pepsico-products-mcp-conn",
  "type": "Microsoft.MachineLearningServices/workspaces/connections",
  "properties": {
    "authType": "ProjectManagedIdentity",
    "category": "RemoteTool",
    "target": "https://pepsico-products-mcp.<env>.azurecontainerapps.io/mcp",
    "audience": "https://management.azure.com/",
    "isSharedToAll": true,
    "metadata": { "ApiType": "MCP" }
  }
}
```

## Optional standalone run

If you want to create the connection without creating the agent, run:

```powershell
python - <<'PY'
from src.common.foundry_client import upsert_project_connection
from src.common.settings import get_settings
s = get_settings()
upsert_project_connection(
    connection_name=s.products_mcp_connection_name,
    category="RemoteTool",
    target=s.products_mcp_url,
    auth_type="ProjectManagedIdentity",
    audience="https://management.azure.com/",
    metadata={"ApiType": "MCP"},
)
print("ok")
PY
```

## Success criteria

{: .success }
> - The Foundry portal **Management center → Connections** shows
>   `pepsico-products-mcp-conn` of type **Remote tool** with the correct target

## Next

[04.02 — Create the Products Foundry agent](04_02_create_products_agent.md).

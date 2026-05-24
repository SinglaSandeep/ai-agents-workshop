---
title: '1. Register the MCP project connection'
layout: default
nav_order: 1
parent: 'Exercise 03: Products Foundry Agent'
---

# Task 03.01 — Register the Products MCP as a Foundry Project Connection

## Introduction

Foundry agents call external tools through **project connections**. A
connection is a Foundry-managed binding that says *"my project is allowed to
talk to this URL, using this auth, with this metadata"*. For MCP tools you
need a `RemoteTool` connection that points at the public MCP endpoint of the
container app (or your localhost tunnel).

Once the connection exists, the agent simply references it by name — the
agent never sees a URL or a credential.

This task creates the connection **directly** so you can verify it in the
Foundry portal before writing any agent code. Task 03.02 will then just
reference it by name.

## Success Criteria

* A connection named `zava-products-mcp-conn` exists on your Foundry
  project (visible in the portal under **Project settings → Connections**).
* Its target equals the `PRODUCTS_MCP_URL` from your `.env`.
* `authType` is `ProjectManagedIdentity` and `category` is `RemoteTool`.

## Key Tasks

### 01: Confirm the required environment variables

The connection lives on a specific Foundry project, so the helper needs
the project's full ARM resource id plus the MCP URL.

```powershell
# Re-hydrate the shell if you opened a new terminal.
Get-Content .env | Where-Object { $_ -and $_ -notmatch '^\s*#' } | ForEach-Object {
    $n, $v = $_ -split '=', 2
    if ($n -and $v) {
        [Environment]::SetEnvironmentVariable($n.Trim(), $v.Trim().Trim('"'), 'Process')
    }
}

$env:AZURE_AI_PROJECT_RESOURCE_ID
$env:PRODUCTS_MCP_URL
```

Both lines must print non-empty values. If `PRODUCTS_MCP_URL` is empty,
use the **local** server URL from Task 02.03
(`http://127.0.0.1:8001/mcp`) — the Foundry agent still works against it
as long as a tunnel (e.g. `devtunnel` or `ngrok`) is forwarding the port,
or you completed the optional deploy in Task 02.04.

### 02: Skim the helper that does the work

Open [src/common/foundry_client.py](https://github.com/SinglaSandeep/ai-agents-workshop/blob/main/src/common/foundry_client.py)
and read `upsert_project_connection`. Key things to notice:

* It does an ARM REST `PUT` to
  `/{projectResourceId}/connections/{name}?api-version=2025-10-01-preview`.
* `category="RemoteTool"` + `metadata={"ApiType": "MCP"}` is the magic
  combo that makes Foundry expose this connection as an MCP-compatible
  tool source.
* `auth_type="ProjectManagedIdentity"` means the project's managed
  identity authenticates outbound calls — no shared secret to manage.
* The function is idempotent (PUT). Re-running it just overwrites the
  target, which is exactly what you want when you re-deploy the
  container app and the FQDN changes.

### 03: Create the connection

Run this one-shot Python snippet from the repo root inside your venv —
it imports the helper and registers the connection in your project.

<details markdown="block">
<summary><strong>Expand this section to view the solution</strong></summary>

```powershell
python -c @"
from src.common.foundry_client import upsert_project_connection
from src.common.settings import get_settings

settings = get_settings()
if not settings.products_mcp_url:
    raise SystemExit('PRODUCTS_MCP_URL is empty. Finish Exercise 02 first.')

result = upsert_project_connection(
    connection_name=settings.products_mcp_connection_name,
    category='RemoteTool',
    target=settings.products_mcp_url,
    auth_type='ProjectManagedIdentity',
    audience='https://management.azure.com/',
    metadata={'ApiType': 'MCP'},
)
print('Created/updated connection:', result['name'])
print('  target :', result['properties']['target'])
print('  category:', result['properties']['category'])
"@
```

Expected output:

```
INFO Upserting Foundry project connection zava-products-mcp-conn
Created/updated connection: zava-products-mcp-conn
  target : https://zava-products-mcp.<env-hash>.<region>.azurecontainerapps.io/mcp
  category: RemoteTool
```

</details>

### 04: Verify in the Foundry portal

Open https://ai.azure.com → your project → **Project settings →
Connections**. You should see `zava-products-mcp-conn` with:

* **Type**: `Remote tool` (or `Custom keys`, depending on portal locale)
* **Target**: matches `PRODUCTS_MCP_URL`
* **Authentication**: Project managed identity

You can also list it via the CLI:

```powershell
$PROJ = $env:AZURE_AI_PROJECT_RESOURCE_ID
az rest --method GET `
  --url "https://management.azure.com$PROJ/connections/zava-products-mcp-conn?api-version=2025-10-01-preview" `
  --query "{name:name, target:properties.target, category:properties.category, auth:properties.authType}" `
  -o table
```

> .note
> Task 03.02 (`create_products_agent.py`) **also** calls
> `upsert_project_connection` so the agent script is self-contained for
> CI runs. Re-running it is safe — the PUT is idempotent and the second
> call simply re-asserts the same target.

## Next

Continue to [03.02 — Create the Products Prompt Agent](03_02_create_products_agent.md).

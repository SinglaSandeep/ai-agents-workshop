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
container app.

Once the connection exists, the agent simply references it by name — the
agent never sees a URL or a credential.

## Success Criteria

* A connection named `pepsico-products-mcp-conn` exists on your Foundry
  project.
* Its target equals the `PRODUCTS_MCP_URL` from your `.env`.
* `authType` is `ProjectManagedIdentity`.

## Key Tasks

### 01: Confirm `PRODUCTS_MCP_URL`

```powershell
$env:PRODUCTS_MCP_URL
```

It should look like `https://pepsico-products-mcp.<env-hash>.<region>.azurecontainerapps.io/mcp`.
If empty, finish Exercise 02 first.

### 02: Read `upsert_project_connection`

Open [src/common/foundry_client.py](../../src/common/foundry_client.py) and
read the `upsert_project_connection` helper. It does an ARM REST `PUT` to
`/connections/{name}` on the Foundry project resource id.

You will not write any code in this task — `create_products_agent.py`
(next task) calls this helper for you. It is enough to understand that:

* `category="RemoteTool"` tells Foundry to expose it as an MCP-compatible tool.
* `auth_type="ProjectManagedIdentity"` means the project's managed identity
  authenticates outbound calls — no shared secret to manage.
* `audience="https://management.azure.com/"` matches the ACA ingress audience.

## Next

Continue to [03.02 — Create the Products Prompt Agent](03_02_create_products_agent.md).

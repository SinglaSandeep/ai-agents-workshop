---
title: '3. Run the server locally'
layout: default
nav_order: 3
parent: 'Exercise 01: Products MCP Server'
---

# Task 01.03 — Run the Products MCP Server Locally

## Steps

1. **Start the server**

   ```powershell
   pepsico-products-mcp
   ```

   You should see `Uvicorn running on http://0.0.0.0:8001`.

2. **List the advertised tools with the MCP inspector**

   In a second terminal:

   ```powershell
   npx -y @modelcontextprotocol/inspector --transport streamable-http http://127.0.0.1:8001/mcp
   ```

   The inspector opens a local UI. Pick **Tools → List** and confirm you see
   `list_categories`, `list_products`, `get_product`, and `search_products`.

3. **Invoke a tool directly with `curl`** (no inspector needed)

   MCP `tools/call` is a JSON-RPC POST:

   ```powershell
   $body = @{
     jsonrpc = "2.0"
     id      = 1
     method  = "tools/call"
     params  = @{
       name      = "search_products"
       arguments = @{ text = "Gatorade"; limit = 3 }
     }
   } | ConvertTo-Json -Depth 6

   curl -s -X POST http://127.0.0.1:8001/mcp `
     -H "Content-Type: application/json" `
     -H "Accept: application/json, text/event-stream" `
     -d $body
   ```

   You should see a Gatorade SKU in the response.

4. **Stop the server** with `Ctrl+C` when done.

## Success criteria

{: .success }
> - The server starts on port 8001
> - The MCP inspector lists all four tools and you can invoke each one
> - The `curl` POST returns at least one Gatorade product

## Next

[01.04 — Deploy to Azure Container Apps](01_04_deploy_container_app.md).

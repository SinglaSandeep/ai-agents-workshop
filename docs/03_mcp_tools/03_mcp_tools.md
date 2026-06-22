---
title: 'Exercise 03: Build the MCP Tools'
layout: default
nav_order: 1
parent: 'Module 2: Build the MCP Tools'
has_children: false
---

# Exercise 03 — Build the MCP Tools

## Scenario

In [Module 1](../02_intent_agent/02_intent_agent.md) you built an agent that can
*reason*, but it had no access to Zava's data. **Tools** are how an agent reaches
the outside world, and in this workshop every tool is exposed through the
**Model Context Protocol (MCP)**.

You will build and verify the **three Zava MCP servers** that the specialist
agents in later modules call:

| Server | Port | Answers the question |
| ------ | ---: | -------------------- |
| **Sales** | `8001` | What is selling? |
| **Inventory** | `8002` | Can we fulfil it? |
| **Marketing** | `8003` | What are we promoting? |

By the end you will:
1. Understand the structure of an MCP server (a FastMCP app exposing tools).
2. Run any of the three Zava MCP servers locally.
3. Connect to it with the **MCP Inspector** (a browser UI for MCP servers).
4. Call the tools and verify the Zava data is rich enough for the workshop.
5. (Optional) Deploy a server to Azure Container Apps for the agents to use.

---

## Prerequisites

- Python environment bootstrapped and `.env` pointing at the
  Cosmos account (see [Exercise 00 — Setup & Prerequisites](../00_setup/00_setup.md)).
- **Node.js 18+** (for the MCP Inspector — it runs via `npx`).

---

## 0. Anatomy of an MCP server

Each server lives under `src/mcp_servers/<domain>/` and is a **FastMCP** app.
A tool is just a Python function decorated with `@mcp.tool` — FastMCP turns its
signature and docstring into the schema an agent sees. Open
[src/mcp_servers/sales/server.py](https://github.com/SinglaSandeep/ai-agents-workshop/blob/main/src/mcp_servers/sales/server.py)
and note three things:

- The `@mcp.tool` functions (`revenue_summary`, `monthly_trend`, …) — these are
  the **tools** the agent can call.
- Each tool queries **Cosmos DB** and returns plain JSON — no agent logic here.
- `app = mcp.streamable_http_app()` exposes the tools at `/mcp` over HTTP.

The Inventory and Marketing servers follow the same shape. You don't have to
write new code — your job in this exercise is to **run** each server and
**verify** its tools behave.

---

## 1. Run an MCP server locally

Each server is a FastMCP app exposing a **streamable-HTTP** endpoint at
`/mcp`. The servers enforce **HTTP Basic auth**, so they read
`MCP_BASIC_AUTH_USERNAME` and `MCP_BASIC_AUTH_PASSWORD` (plus the Cosmos DB
settings) from the environment at startup. `uvicorn` does **not** auto-load your
`.env`, so pass it with `--env-file` — otherwise the server fails with
`RuntimeError: MCP_BASIC_AUTH_USERNAME must be set to enable MCP Basic Auth.`

Start whichever server you want to test:

```powershell
# Sales insights  → http://localhost:8001/mcp
uvicorn src.mcp_servers.sales.server:app --port 8001 --env-file .env

# Inventory health → http://localhost:8002/mcp
uvicorn src.mcp_servers.inventory.server:app --port 8002 --env-file .env

# Marketing campaigns → http://localhost:8003/mcp
uvicorn src.mcp_servers.marketing.server:app --port 8003 --env-file .env
```

Leave the server running in its own terminal.

---

## 2. Connect with the MCP Inspector

In a **second** terminal, launch the Inspector (leave the server running in the
first one):

```powershell
npx @modelcontextprotocol/inspector
```

The terminal prints a URL with a session token and opens a browser tab, e.g.:

```
🔗 Open inspector with token pre-filled:
   http://localhost:6274/?MCP_PROXY_AUTH_TOKEN=abc123...
```

If the tab doesn't open, copy that full URL (with the token) into your browser.

Then, in the Inspector UI:

1. **Transport Type** → select **Streamable HTTP**.
2. **URL** → enter `http://localhost:8001/mcp` (use `8002` for inventory,
   `8003` for marketing).
3. Expand **Authentication** → **Custom Headers** and add one header (the
   servers require Basic auth, so without it Connect returns `401`):
   - **Name**: `Authorization`
   - **Value**: copy the ready-made `Basic …` value from the
     **Foundry MCP connection** note in your `.env`.
   Keep the header toggle **enabled**.
4. Click **Connect**. The status dot turns green.
5. Open the **Tools** tab → click **List Tools**.
6. Pick a tool (e.g. `monthly_trend`), fill in its arguments
   (e.g. `category` = `paint`), then click **Run Tool**.
7. Read the JSON in the **Response** pane — that's exactly what the agent
   receives.

Prefer the terminal? Skip the UI entirely and call tools headless:

```powershell
# List the tools a server exposes (pass the Basic auth header the server requires;
# copy the Basic … value from your .env)
npx @modelcontextprotocol/inspector --cli http://localhost:8001/mcp `
  --header "Authorization: Basic <value from .env>" --method tools/list

# Call one tool with arguments
npx @modelcontextprotocol/inspector --cli http://localhost:8001/mcp `
  --header "Authorization: Basic <value from .env>" `
  --method tools/call --tool-name monthly_trend --tool-arg category=paint
```

---

## 3. What each team can test

Each server exposes a few tools. Connect to a server in the Inspector, click
**List Tools**, then try one of the examples below.

| Server (`port`) | Try this tool | With these arguments |
| --------------- | ------------- | -------------------- |
| **Sales** (`:8001`) | `monthly_trend` | `category="paint"` |
| **Inventory** (`:8002`) | `inventory_for_product` | `product_id="ZV-PNT-001"` |
| **Marketing** (`:8003`) | `get_campaign` | `campaign_id="ZV-CMP-2026-001"` |

Call **List Tools** on each server to see everything it offers. The three
servers share the same keys (`store_id`, `category_id`, `product_id`), so their
results line up into one story.

### Try the end-to-end check

Run these three tools in order and you reproduce, by hand, what the orchestrator
does automatically:

1. **Sales** `monthly_trend` with `category="paint"` → paint sales are **softening**.
2. **Inventory** `inventory_for_product` with `product_id="ZV-PNT-001"` → Seattle
   stock cover is **critically low**.
3. **Marketing** `get_campaign` with `campaign_id="ZV-CMP-2026-001"` → a 20%-off
   promo is **active** at Seattle.

➡️ **The insight:** a discount is driving demand for a paint product that
Seattle is about to run out of — so pre-position `ZV-PNT-001` at Seattle and
raise its reorder threshold.

---

## Data volumes you should see

If the Cosmos containers are seeded, the tools draw on:

| Container | Approx. rows | Shape |
| --------- | -----------: | ----- |
| `sales` | **~1,200** order lines | 12 rolling months, seasonal trends |
| `inventory` | **~1,700** snapshots | 6 weekly snapshots × 6 warehouses × 48 SKUs |
| `marketing` | **~1,200** campaigns | curated headline set + multi-year history |

All three containers share the same **48-SKU product catalog** (6 per category),
defined in code — it is not a separate container.

If a tool returns empty, re-seed with the workshop seed commands
(`zava-seed-sales`, `zava-seed-inventory`, `zava-seed-marketing`).

---

## 4. (Optional) Deploy a server to Azure Container Apps

Locally-run servers are perfect for this workshop, but the Foundry agents in
later modules reach their tools over a public URL. Each server ships with a
`Dockerfile` so you can deploy it to **Azure Container Apps** and record its
URL in `.env`:

```powershell
# Example: deploy the Sales MCP server
az containerapp up `
  --name zava-sales-mcp `
  --resource-group <your-rg> `
  --source src/mcp_servers/sales
```

Save each public URL plus `/mcp` to `.env` so the agents can find them:

```dotenv
SALES_MCP_URL=https://zava-sales-mcp.<region>.azurecontainerapps.io/mcp
INVENTORY_MCP_URL=https://zava-inventory-mcp.<region>.azurecontainerapps.io/mcp
MARKETING_MCP_URL=https://zava-marketing-mcp.<region>.azurecontainerapps.io/mcp
```

### Authentication

The deployed servers are **not open to the public** — `src/common/basic_auth.py`
wraps each one in HTTP **Basic auth**, reading `MCP_BASIC_AUTH_USERNAME` and
`MCP_BASIC_AUTH_PASSWORD` from the container environment. Keep both set in `.env`
(the deploy scripts pass them through as Container App secrets).

When you wire a server into a Foundry agent (Modules 4–6), choose **Key-based**
authentication and add a single credential header:

| Field | Value |
| ----- | ----- |
| Key | `Authorization` |
| Value | `Basic <base64 of MCP_BASIC_AUTH_USERNAME:MCP_BASIC_AUTH_PASSWORD>` |

Generate the header value from the credentials already in your `.env`:

```powershell
python -c "import base64,os;u=os.environ['MCP_BASIC_AUTH_USERNAME'];p=os.environ['MCP_BASIC_AUTH_PASSWORD'];print('Basic '+base64.b64encode(f'{u}:{p}'.encode()).decode())"
```

> Skipping deployment? Keep the servers running locally and point the
> `*_MCP_URL` values at `http://localhost:<port>/mcp`. Every later module works
> either way.

---

## Success criteria

{: .success }
> - At least one MCP server runs locally and the Inspector lists its tools.
> - `revenue_summary`, `low_stock`, and `list_active_campaigns` each return
>   non-empty JSON.
> - The three-step killer query above returns soft paint sales + low Seattle
>   cover + an active paint promo.

## References

- [Model Context Protocol — specification](https://modelcontextprotocol.io/)
- [MCP Python SDK](https://github.com/modelcontextprotocol/python-sdk)
- [MCP Inspector](https://github.com/modelcontextprotocol/inspector)
- [Use the Model Context Protocol (MCP) tool in Foundry](https://learn.microsoft.com/azure/ai-foundry/agents/how-to/tools/model-context-protocol)

## Next

Continue to
[Exercise 04 — Build the Sales Agent](../04_sales_agent/04_sales_agent.md),
where you connect a Foundry agent to the Sales MCP tool you just built.

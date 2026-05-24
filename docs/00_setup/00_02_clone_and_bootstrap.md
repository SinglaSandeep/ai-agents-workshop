---
title: '2. Clone and bootstrap the repo'
layout: default
nav_order: 2
parent: 'Exercise 00: Setup & Verify Resources'
---

# Task 00.02 — Clone and Bootstrap the Workshop

## Steps

1. **Clone the [repo](https://github.com/SinglaSandeep/ai-agents-workshop) and `cd` into it**

   ```powershell
   git clone https://github.com/SinglaSandeep/ai-agents-workshop.git
   cd ai-agents-workshop
   ```

2. **Create a virtual environment and activate it**

   ```powershell
   python -m venv .venv
   .\.venv\Scripts\Activate.ps1
   ```

   {: .note }
   > On macOS/Linux use `source .venv/bin/activate` instead.

3. **Install the workshop package (with all extras)**

   ```powershell
   python -m pip install --upgrade pip
   python -m pip install -e ".[dev,framework,observability,mcp,evals,redteam,hosted]"
   ```

   #### Why `-e` (editable)?

   The whole workshop is built on **scaffold-and-fill-in**: you edit TODOs
   in `src/...` as you progress through the exercises. The `-e` flag drops
   a `.pth` link to your working tree instead of copying files into
   `site-packages`, so your edits are picked up immediately — no
   `pip install` between every change.

   #### What each extra installs and where it is used

   The **base install** (no extras) gives you the always-needed runtime
   that every exercise relies on:

   | Package | Used for |
   | ------- | -------- |
   | `fastapi`, `uvicorn[standard]` | The chat-app HTTP server (Exercise 01 onward) |
   | `pydantic`, `pydantic-settings`, `python-dotenv` | `.env` → typed `Settings` object (Exercise 00 onward) |
   | `azure-identity` | `DefaultAzureCredential` / `ChainedTokenCredential` for every Azure call |
   | **`azure-cosmos`** | Cosmos DB SDK — seeds the `products` and `marketing_campaigns` containers in Exercises **02** and **04** and is the data source for both MCP servers |
   | `azure-ai-projects`, `azure-core` | Foundry project client used by every agent script |
   | `openai` | Direct OpenAI / Azure OpenAI client used by evaluations and the response generator |
   | `httpx`, `requests` | HTTP calls (KB REST, MCP smoke tests) |

   The extras add the per-module dependencies on top:

   | Extra | Packages it brings in | First exercise that needs it |
   | ----- | --------------------- | ---------------------------- |
   | `dev` | `pytest`, `pytest-asyncio`, `ruff` | **00** — run the smoke tests + lint as you go |
   | `mcp` | `mcp`, `fastmcp` | **02** — build the Products MCP server (and **04** for Marketing) |
   | `framework` | `agent-framework-core`, `agent-framework-azure-ai` | **03** — call Foundry agents from Python (and **06**, **07**) |
   | `hosted` | `agent-framework-foundry-hosting`, `mcp` | **05** — host the Marketing agent on Foundry (`ResponsesHostServer`) |
   | `observability` | `azure-monitor-opentelemetry`, `opentelemetry-api`/`-sdk`, FastAPI + httpx OTel instrumentors | **11** — chat-app traces to App Insights |
   | `evals` | `azure-ai-evaluation` | **09** — quality + scheduled + continuous evaluations |
   | `redteam` | `azure-ai-evaluation[redteam]`, `rich` | **10** — automated adversarial scan |

   {: .tip }
   > If you want a leaner first install you can start with just
   > `".[dev,framework,mcp]"` for Exercises 00–04 and add the rest
   > later (`pip install -e ".[hosted,evals,redteam,observability]"`)
   > when you reach those modules.

   {: .note }
   > The full install pulls roughly 150 MB of wheels (mostly Azure SDKs
   > and OpenTelemetry instrumentation). On a slow link, start with the
   > lean variant above so you can begin Exercise 01 sooner.

4. **Copy `.env.sample` to `.env`**

   ```powershell
   Copy-Item .env.sample .env
   ```

5. **Sign in to Azure**

   ```powershell
   az login
   az account set --subscription "<your-subscription-id>"
   az account show --output table
   ```

## Success criteria

{: .success }
> - `pip show pepsico-ai-agents-workshop` prints the package metadata
> - `python -c "from src.common.settings import get_settings; print(get_settings().model_dump_json(indent=2))"` runs (most values will be empty — you fill them in next)
> - `az account show` returns the workshop subscription

## Next

Continue to [00.03 — Verify pre-provisioned resources](00_03_verify_resources.md).

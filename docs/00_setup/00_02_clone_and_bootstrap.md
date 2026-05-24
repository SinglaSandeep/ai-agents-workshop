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
   python -m pip install --pre -e ".[dev,framework,observability,mcp,evals,redteam]"
   ```

   {: .important }
   > The `--pre` flag is required because the `framework` extra pins
   > `agent-framework-orchestrations==1.0.0rc2` (Magentic / handoff /
   > sequential builders), which is still published as a release
   > candidate on PyPI. Without `--pre`, pip refuses to install it and
   > Exercise 07 will fail with
   > `ModuleNotFoundError: agent_framework_orchestrations`.

   {: .note }
   > The `hosted` extra is intentionally **not** installed here. The
   > `agent-framework-foundry-hosting` package is currently only published
   > as a pre-release on PyPI, so attempting to install it as part of the
   > default bootstrap fails with
   > `No matching distribution found for agent-framework-foundry-hosting`.
   > You will install it explicitly in **Exercise 05** with
   > `pip install --pre "agent-framework-foundry-hosting>=0.3.0a0"`.

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
   | `dev` | `ruff` | **00** — keep your scaffold edits lint-clean |
   | `mcp` | `mcp`, `fastmcp` | **02** — build the Products MCP server (and **04** for Marketing) |
   | `framework` | `agent-framework-core==1.6.0`, `agent-framework-foundry==1.6.0`, `agent-framework-orchestrations==1.0.0rc2` (pre-release), `agent-framework-devui==1.0.0b260521` (pre-release — provides the workshop's frontend) | **01** — DevUI frontend; **03** — call Foundry agents from Python (and **06**, **07**) |
   | `hosted` | `mcp` (+ pre-release `agent-framework-foundry-hosting`, installed separately in Exercise 05) | **05** — host the Marketing agent on Foundry (`ResponsesHostServer`) |
   | `observability` | `azure-monitor-opentelemetry`, `opentelemetry-api`/`-sdk`, FastAPI + httpx OTel instrumentors | **11** — chat-app traces to App Insights |
   | `evals` | `azure-ai-evaluation` | **09** — quality + scheduled + continuous evaluations |
   | `redteam` | `azure-ai-evaluation[redteam]`, `rich` | **10** — automated adversarial scan |

   {: .tip }
   > If you want a leaner first install you can start with just
   > `pip install --pre -e ".[dev,framework,mcp]"` for Exercises 00–04
   > and add the rest later
   > (`pip install -e ".[evals,redteam,observability]"`) when you reach
   > those modules. The `hosted` extra is installed separately in
   > Exercise 05 with the `--pre` flag (see note above).

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
> - `pip show zava-ai-agents-workshop` prints the package metadata
> - `python -c "from src.common.settings import get_settings; print(get_settings().model_dump_json(indent=2))"` runs (most values will be empty — you fill them in next)
> - `az account show` returns the workshop subscription

## Next

Continue to [00.03 — Verify pre-provisioned resources](00_03_verify_resources.md).

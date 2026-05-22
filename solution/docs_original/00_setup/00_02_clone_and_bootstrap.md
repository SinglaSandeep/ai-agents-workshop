---
title: '2. Clone and bootstrap the repo'
layout: default
nav_order: 2
parent: 'Exercise 00: Setup & Verify Resources'
---

# Task 00.02 — Clone and Bootstrap the Workshop

## Steps

1. **Clone the repo and `cd` into it**

   ```powershell
   git clone https://github.com/<your-org>/ai-agents-workshop.git
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
   python -m pip install -e ".[dev,framework,observability,mcp]"
   ```

   This installs:
   - the workshop package in **editable** mode (so you can hack on the code)
   - the **MCP** stack (`fastmcp`, `mcp`)
   - the **Microsoft Agent Framework** stack
   - **observability** (OpenTelemetry + Azure Monitor exporter)
   - **dev** tools (pytest, ruff)

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

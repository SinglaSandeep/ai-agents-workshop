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

3. **Install all workshop dependencies from `requirements.txt`**

   ```powershell
   python -m pip install --upgrade pip
   python -m pip install --pre -r requirements.txt
   ```

   That's it — one flat list of pinned versions, no editable install, no
   extras to remember. The file lives at the repo root and covers every
   exercise (chat app, MCP servers, Agent Framework, Foundry hosting,
   observability, evaluations, red teaming).

   {: .important }
   > The `--pre` flag is required because a few packages are still
   > published as pre-releases on PyPI:
   > `agent-framework-orchestrations==1.0.0rc2` (Magentic builder used in
   > Exercise 07), `agent-framework-devui==1.0.0b260521` (the workshop
   > frontend), and `agent-framework-foundry-hosting==0.3.0a0` (used to
   > host the Marketing agent in Exercise 05). Without `--pre`, pip will
   > refuse to install them.

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
> - `python -c "import fastapi, agent_framework, mcp; print('ok')"` prints `ok`
> - `python -c "from src.common.settings import get_settings; print(get_settings().model_dump_json(indent=2))"` runs (most values will be empty — you fill them in next)
> - `az account show` returns the workshop subscription

## Next

Continue to [00.03 — Verify pre-provisioned resources](00_03_verify_resources.md).

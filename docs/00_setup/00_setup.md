---
title: 'Exercise 00: Setup & Prerequisites'
layout: default
nav_order: 1
parent: 'Setup & Prerequisites'
---

# Exercise 00 — Setup & Prerequisites

This page gets your machine ready in four simple steps: **install the tools**,
**clone the workshop**, **set up Python**, and **create your `.env` file**.
No prior experience required — just follow the steps in order.

{: .note }
> Your platform team has already created all the Azure resources for you. You do
> **not** provision anything here — you only install local tools and point the
> workshop at the resources you were given.

## Success criteria

{: .success }
> By the end of this page:
> - `python --version` returns 3.11 or higher.
> - `az account show` returns your workshop subscription.
> - You have a populated `.env` file at the repo root.

---

## Step 1 — Install the local tools

You need five tools on your machine. **No local container runtime is required.**

| Tool | Min version | Download | Purpose |
| ---- | ----------- | -------- | ------- |
| **Python** | 3.11 | [python.org/downloads](https://www.python.org/downloads/) | Workshop runtime + Foundry SDK |
| **Git** | 2.40 | [git-scm.com/downloads](https://git-scm.com/downloads) | Cloning the workshop repo |
| **Azure CLI (`az`)** | 2.61 | [aka.ms/installazurecli](https://learn.microsoft.com/cli/azure/install-azure-cli) | Sign in + deploys |
| **VS Code** | latest | [code.visualstudio.com](https://code.visualstudio.com/Download) | Editor (any IDE works) |
| **PowerShell 7** (Win) / **bash** (mac/Linux) | — | [aka.ms/powershell](https://learn.microsoft.com/powershell/scripting/install/installing-powershell) | Terminal |

{: .note }
> **Windows shortcut** — install everything at once with
> [winget](https://learn.microsoft.com/windows/package-manager/winget/):
>
> ```powershell
> winget install Python.Python.3.12 Git.Git Microsoft.AzureCLI Microsoft.VisualStudioCode Microsoft.PowerShell
> ```
>
> Keep **"Add python.exe to PATH"** checked.

Then add the Container Apps CLI extension (used later when you deploy):

```powershell
az extension add --name containerapp --upgrade
```

**Recommended VS Code extension:** open the **Extensions** panel
(**Ctrl+Shift+X** / **Cmd+Shift+X**), search for
[Python](https://marketplace.visualstudio.com/items?itemName=ms-python.python),
and click **Install**. This adds the ▶ Run button and picks your virtual
environment automatically.

Check the tools are ready:

```powershell
python --version   # ≥ 3.11
git --version      # ≥ 2.40
az --version       # ≥ 2.61
```

---

## Step 2 — Clone the workshop

```powershell
git clone https://github.com/SinglaSandeep/ai-agents-workshop.git
cd ai-agents-workshop
```

---

## Step 3 — Set up Python

Create an isolated virtual environment and install the workshop dependencies.

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install --pre -r requirements.txt
```

{: .note }
> On **macOS/Linux** activate with `source .venv/bin/activate` instead.

{: .important }
> The `--pre` flag is required — a few Agent Framework packages are still
> published as pre-releases on PyPI, and pip refuses to install them without it.

---

## Step 4 — Create your `.env` file

The workshop reads its settings from a file named `.env` at the repo root.
Start from the provided template and fill in your values.

1. **Copy the template to `.env`:**

   ```powershell
   Copy-Item .env.sample .env
   ```

   {: .note }
   > On **macOS/Linux** use `cp .env.sample .env`.

2. **Open `.env` and fill in the blanks.** The file is a plain list of
   `NAME=value` lines. Each blank value (the part after the `=`) gets a value
   your platform team gave you. For example, change:

   ```dotenv
   COSMOS_ENDPOINT=
   ```

   to:

   ```dotenv
   COSMOS_ENDPOINT=https://zava-cosmos.documents.azure.com:443/
   ```

   Fill in at least these core values (your platform team provides them, or you
   can copy them from the Azure portal):

   | Variable | What it is |
   | -------- | ---------- |
   | `AZURE_SUBSCRIPTION_ID` | Your Azure subscription id |
   | `AZURE_TENANT_ID` | Your Azure tenant id |
   | `AZURE_RESOURCE_GROUP` | Resource group holding the workshop resources |
   | `AZURE_AI_PROJECT_ENDPOINT` | Microsoft Foundry project endpoint URL |
   | `AZURE_AI_MODEL_DEPLOYMENT` | Model deployment name (e.g. `gpt-4.1-mini`) |
   | `AZURE_SEARCH_ENDPOINT` | Azure AI Search endpoint URL |
   | `COSMOS_ENDPOINT` | Azure Cosmos DB account endpoint URL |
   | `ACR_NAME` | Azure Container Registry name |

   {: .note }
   > Leave the other lines as-is — variables for the MCP servers and
   > observability get filled in automatically during later exercises. Lines that
   > already have a default value can stay unchanged.

   {: .important }
   > **Never commit `.env`.** It can contain secrets. It is already listed in
   > `.gitignore`, so git ignores it for you — keep it that way.

3. **Sign in to Azure** so the workshop can reach your resources:

   ```powershell
   az login
   az account set --subscription "<your-subscription-id>"
   az account show --output table
   ```

---

## You're ready

That's it — your environment is set up. Continue to
[Exercise 01 — Scaffold the Chat App](../01_chat_app_scaffold/01_chat_app_scaffold.md).

## References

- [What is Microsoft Foundry?](https://learn.microsoft.com/azure/ai-foundry/what-is-azure-ai-foundry)
- [Install the Azure CLI](https://learn.microsoft.com/cli/azure/install-azure-cli)
- [Sign in with the Azure CLI (`az login`)](https://learn.microsoft.com/cli/azure/authenticate-azure-cli)
- [Reference Architecture](../architecture.md)
- [ai-agents-workshop on GitHub](https://github.com/SinglaSandeep/ai-agents-workshop)

---
title: '1. Local prerequisites'
layout: default
nav_order: 1
parent: 'Exercise 00: Setup & Verify Resources'
---

# Task 00.01 — Install Local Prerequisites

You need the following tools on your machine. **No local container runtime
is required** — the MCP server images in Exercises 02 and 04 are built in
the cloud by Azure Container Registry, and the hosted Marketing agent
image in Exercise 05 is built by `azd ai agent up` against your Foundry
account.

| Tool | Minimum version | Purpose |
| ---- | --------------- | ------- |
| **Python** | 3.11 | Workshop runtime + Foundry SDK |
| **pip / venv** | (bundled) | Package management |
| **Git** | 2.40 | Cloning the workshop repo |
| **Azure CLI (`az`)** | 2.61 | Authentication + Container Apps deploys (cloud build) |
| **Azure Developer CLI (`azd`)** | 1.10 | Hosted-agent deploys (`azd ai agent up`, from Exercise 05) |
| **Visual Studio Code** | latest | Editor (any IDE works; VS Code is recommended) |
| **PowerShell 7** (Windows) or **bash** (mac/Linux) | — | Terminal |

## Steps

1. **Verify Python 3.11+**

   ```powershell
   python --version
   ```

   If you need to install it, grab the latest 3.12 release from
   <https://www.python.org/downloads/> and make sure
   **"Add python.exe to PATH"** is checked.

2. **Install / update the Azure CLI**

   ```powershell
   winget install --id Microsoft.AzureCLI
   # or upgrade an existing install
   az upgrade
   ```

   Then add the Container Apps extension and register the providers used
   by Exercises 02 and 04:

   ```powershell
   az extension add --name containerapp --upgrade
   az provider register --namespace Microsoft.App
   az provider register --namespace Microsoft.OperationalInsights
   ```

3. **Install the Azure Developer CLI (`azd`) + AI extension**

   ```powershell
   winget install --id Microsoft.Azd
   azd version
   azd extension install ai
   ```

   You will use `azd ai agent run`, `azd ai agent invoke` and
   `azd ai agent up` from Exercise 05 onwards.

4. **Install Git and VS Code** (skip if already installed)

   ```powershell
   winget install --id Git.Git
   winget install --id Microsoft.VisualStudioCode
   ```

5. **VS Code extensions (recommended)**

   - Python
   - Azure Account
   - Azure Resources
   - REST Client (handy for testing the MCP servers)

## Success criteria

{: .success }
> - `python --version` ≥ 3.11
> - `az --version` ≥ 2.61
> - `azd version` ≥ 1.10
> - `azd extension list` shows the **ai** extension
> - VS Code opens

> {: .note }
> Docker Desktop is **not** required for this workshop. `az containerapp
> up --source .` automatically uses an **ACR Task** (cloud build) when no
> local Docker daemon is detected, and `azd ai agent up` builds the
> hosted-agent image inside the Foundry environment.

## Next

Continue to [00.02 — Clone and bootstrap the repo](00_02_clone_and_bootstrap.md).

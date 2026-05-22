---
title: '1. Local prerequisites'
layout: default
nav_order: 1
parent: 'Exercise 00: Setup & Verify Resources'
---

# Task 00.01 — Install Local Prerequisites

You need the following tools on your machine:

| Tool | Minimum version | Purpose |
| ---- | --------------- | ------- |
| **Python** | 3.11 | Workshop runtime + Foundry SDK |
| **pip / venv** | (bundled) | Package management |
| **Git** | 2.40 | Cloning the workshop repo |
| **Azure CLI (`az`)** | 2.61 | Authentication, Container Apps deploys |
| **Docker Desktop** | 4.30 | Build the two MCP server images |
| **Visual Studio Code** | latest | Editor (any IDE works; VS Code is recommended) |
| **PowerShell 7** (Windows) or **bash** (mac/Linux) | — | Terminal |

## Steps

1. **Verify Python 3.11+**

   ```powershell
   python --version
   ```

   If you need to install it, grab the latest 3.12 release from <https://www.python.org/downloads/>
   and make sure **"Add python.exe to PATH"** is checked.

2. **Install / update the Azure CLI**

   ```powershell
   winget install --id Microsoft.AzureCLI
   # or upgrade an existing install
   az upgrade
   ```

   Then add the Container Apps extension:

   ```powershell
   az extension add --name containerapp --upgrade
   az provider register --namespace Microsoft.App
   az provider register --namespace Microsoft.OperationalInsights
   ```

3. **Install Docker Desktop**

   Download from <https://www.docker.com/products/docker-desktop/>. Make sure
   Docker is running before Exercise 01.

   ```powershell
   docker --version
   docker run --rm hello-world
   ```

4. **Install Git and VS Code** (skip if already installed)

   ```powershell
   winget install --id Git.Git
   winget install --id Microsoft.VisualStudioCode
   ```

5. **VS Code extensions (recommended)**

   - Python
   - Azure Account
   - Azure Resources
   - Docker
   - REST Client (handy for testing the MCP servers)

## Success criteria

{: .success }
> - `python --version` ≥ 3.11
> - `az --version` ≥ 2.61
> - `docker run --rm hello-world` prints a success message
> - VS Code opens

## Next

Continue to [00.02 — Clone and bootstrap the repo](00_02_clone_and_bootstrap.md).

---
title: '3. Create the Container App'
layout: default
nav_order: 3
parent: 'Exercise 13: Deploy the Chat App to Container Apps'
---

# Task 13.03 — Create the `zava-chat-app` Container App

## Introduction

You now create the Container App, store the basic-auth password as a
**secret** (so it never appears as a plain env var in the portal), enable
a **system-assigned managed identity**, and pass through every Foundry
endpoint the orchestrator needs.

## Success Criteria

{: .success }
> - `az containerapp show -n zava-chat-app -g $RG --query "properties.provisioningState"` returns `Succeeded`.
> - The app has a system-assigned managed identity (the `principalId` is
>   captured for the next task).
> - `BASIC_AUTH_PASSWORD` shows up under **Secrets**, not under
>   environment variables.

## Key Tasks

### 01: Pick names and capture core values

```powershell
$RG          = $env:AZURE_RESOURCE_GROUP            # e.g. aifounry-rg
$ACR         = $env:ACR_NAME                        # e.g. acrregistry2025
$ENV         = $env:ACA_ENVIRONMENT                 # e.g. pepsico-aca-env
$APP         = "zava-chat-app"
$IMG         = "$ACR.azurecr.io/zava-chat-app:latest"

$BASIC_USER  = "demo-admin"
$BASIC_PWD   = 'M$FT#AI@2026'                       # single quotes — $ is literal

# Foundry / model wiring (copy from .env)
$PROJECT_EP  = $env:AZURE_AI_PROJECT_ENDPOINT
$MODEL       = $env:AZURE_AI_MODEL_DEPLOYMENT       # default manager model

$RG; $ACR; $ENV; $APP; $IMG; $PROJECT_EP; $MODEL
```

All seven lines must be non-empty.

### 02: Create the Container App

```powershell
az containerapp create `
  --name $APP `
  --resource-group $RG `
  --environment $ENV `
  --image $IMG `
  --target-port 8000 `
  --ingress external `
  --system-assigned `
  --secrets "basic-auth-password=$BASIC_PWD" `
  --env-vars `
      BASIC_AUTH_USERNAME=$BASIC_USER `
      BASIC_AUTH_PASSWORD=secretref:basic-auth-password `
      AZURE_AI_PROJECT_ENDPOINT=$PROJECT_EP `
      AZURE_AI_MODEL_DEPLOYMENT=$MODEL `
      ORCHESTRATOR_MODEL_CHOICES="gpt-4.1,gpt-4.1-mini,gpt-4o,gpt-4o-mini" `
  --min-replicas 1 --max-replicas 1
```

> Add any agent-name env vars from `.env` that your orchestrator reads
> (`AZURE_AI_STORE_OPS_AGENT_ID`, `AZURE_AI_PRODUCTS_AGENT_ID`, …) to the
> `--env-vars` list so the container can resolve all four agents.

### 03: Capture the FQDN and managed identity

```powershell
$FQDN = az containerapp show -n $APP -g $RG `
  --query "properties.configuration.ingress.fqdn" -o tsv
$MI   = az containerapp show -n $APP -g $RG `
  --query "identity.principalId" -o tsv
$FQDN; $MI
```

You will use `$MI` in [13.04](13_04_grant_roles.md).

## Troubleshooting

| Symptom | Fix |
| ------- | --- |
| `Failed to provision revision … ImagePullBackOff` | The managed identity does not yet have **AcrPull** — see 13.04. |
| `$PROJECT_EP` is empty | You forgot to re-hydrate from `.env` in this shell. |
| Two revisions appear | Container Apps creates a new revision per change — that is fine. The latest one is the active one. |

## Next

Continue to [13.04 — Grant Foundry roles to the MI](13_04_grant_roles.md).

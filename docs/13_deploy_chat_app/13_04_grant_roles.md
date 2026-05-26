---
title: '4. Grant Foundry roles to the managed identity'
layout: default
nav_order: 4
parent: 'Exercise 13: Deploy the Chat App to Container Apps'
---

# Task 13.04 — Grant `AcrPull` + Foundry data-plane roles

## Introduction

The Container App's system-assigned managed identity (MI) needs three
role assignments before the chat app can start serving requests:

| Scope | Role | Why |
| ----- | ---- | --- |
| ACR (`Microsoft.ContainerRegistry/registries/<acr>`) | **AcrPull** | Pull the image on cold-start. |
| Foundry account (`Microsoft.CognitiveServices/accounts/<foundry>`) | **Azure AI Developer** | Run agents, list deployments, stream chat completions. |
| Same Foundry account | **Cognitive Services User** | Data-plane access to the model deployments themselves. |

> "Azure AI User" is **not** a real built-in role — use **Azure AI Developer**.

## Success Criteria

{: .success }
> - All three `az role assignment create` calls return without error.
> - `az role assignment list --assignee $MI -o table` shows the three
>   roles on the expected scopes.

## Key Tasks

### 01: Re-capture identifiers

```powershell
$RG          = $env:AZURE_RESOURCE_GROUP
$ACR         = $env:ACR_NAME
$ACR_RG      = "<the RG that owns the ACR>"          # often different from $RG
$FOUNDRY     = "<your Foundry account name>"         # e.g. foundry-workshop-sc
$FOUNDRY_RG  = "<the RG that owns the Foundry account>"
$SUB         = $env:AZURE_SUBSCRIPTION_ID

$MI = az containerapp show -n zava-chat-app -g $RG --query "identity.principalId" -o tsv
$MI
```

### 02: Grant `AcrPull` on the registry

```powershell
$ACR_SCOPE = "/subscriptions/$SUB/resourceGroups/$ACR_RG/providers/Microsoft.ContainerRegistry/registries/$ACR"

az role assignment create `
  --assignee-object-id $MI `
  --assignee-principal-type ServicePrincipal `
  --role "AcrPull" `
  --scope $ACR_SCOPE
```

### 03: Grant Foundry data-plane roles

```powershell
$FOUNDRY_SCOPE = "/subscriptions/$SUB/resourceGroups/$FOUNDRY_RG/providers/Microsoft.CognitiveServices/accounts/$FOUNDRY"

az role assignment create `
  --assignee-object-id $MI `
  --assignee-principal-type ServicePrincipal `
  --role "Azure AI Developer" `
  --scope $FOUNDRY_SCOPE

az role assignment create `
  --assignee-object-id $MI `
  --assignee-principal-type ServicePrincipal `
  --role "Cognitive Services User" `
  --scope $FOUNDRY_SCOPE
```

### 04: Restart the revision so the MI picks up the roles

Role propagation typically takes 30–60 seconds. Restart the latest
revision so the pod re-authenticates:

```powershell
$rev = az containerapp show -n zava-chat-app -g $RG `
  --query "properties.latestRevisionName" -o tsv
az containerapp revision restart -n zava-chat-app -g $RG --revision $rev
```

## Troubleshooting

| Symptom | Fix |
| ------- | --- |
| `The role assignment already exists.` | Idempotent — safe to ignore. |
| `Principal ... does not exist in the directory.` | The MI is brand new; wait 30 s and retry. |
| Container logs show `403 Forbidden` against Foundry | One of the two Foundry roles is missing or scoped to the wrong account. Use the **full** account resource ID, not just the name. |

## Next

Continue to [13.05 — Verify and update](13_05_verify_and_update.md).

---
title: '5. Verify, swap models live, and update'
layout: default
nav_order: 5
parent: 'Exercise 13: Deploy the Chat App to Container Apps'
---

# Task 13.05 — Verify the deployment, swap models live, redeploy

## Introduction

The image is built, the app is created, and the MI has its roles.
Now confirm everything works end-to-end, demo the runtime model picker,
and learn the one-command redeploy loop you will use during the workshop.

## Success Criteria

{: .success }
> - `GET /health` returns 200.
> - `GET /` without credentials returns 401.
> - `GET /` with `demo-admin / M$FT#AI@2026` returns 200 and the chat UI.
> - `GET /models` returns the choices list.
> - Asking a question with `gpt-4.1-mini` selected in the dropdown
>   succeeds, and the orchestrator log shows
>   `manager_model=gpt-4.1-mini`.

## Key Tasks

### 01: Smoke-test the public URL

```powershell
$FQDN = az containerapp show -n zava-chat-app -g $env:AZURE_RESOURCE_GROUP `
  --query "properties.configuration.ingress.fqdn" -o tsv

curl.exe -s -o NUL -w "health   HTTP %{http_code}`n" "https://$FQDN/health"
curl.exe -s -o NUL -w "/        HTTP %{http_code} (no auth)`n" "https://$FQDN/"
curl.exe -s -o NUL -w "/        HTTP %{http_code} (with auth)`n" `
  -u "demo-admin:M`$FT#AI@2026" "https://$FQDN/"
curl.exe -s -u "demo-admin:M`$FT#AI@2026" "https://$FQDN/models"
```

Expected:

```text
health   HTTP 200
/        HTTP 401 (no auth)
/        HTTP 200 (with auth)
{"default":"gpt-4.1","choices":["gpt-4.1","gpt-4.1-mini","gpt-4o","gpt-4o-mini"]}
```

### 02: Open the UI and demo the model picker

1. Open `https://<fqdn>/` in a fresh browser tab.
2. Authenticate with `demo-admin` / `M$FT#AI@2026`.
3. Above the chat input there is now a **model dropdown**. The label
   shows the current default, e.g. `gpt-4.1 (default)`.
4. Pick a different option (e.g. `gpt-4o-mini`).
5. Ask: *"What is our PTO policy?"*
6. In the **Execution Trace** you will see a `START` event whose payload
   includes `"manager_model":"gpt-4o-mini"`.
7. Switch back to `gpt-4.1`, ask again, and notice the manager replans
   under the larger model.

Only the **Magentic manager** is swapped. Hosted Foundry specialists
keep the models configured on their agent definitions.

### 03: Change the dropdown choices without rebuilding

```powershell
az containerapp update -n zava-chat-app -g $env:AZURE_RESOURCE_GROUP `
  --set-env-vars ORCHESTRATOR_MODEL_CHOICES="gpt-4.1,gpt-4o,o3-mini"
```

This bumps the revision; the new options show up on the next page load.

### 04: Iterate on code — rebuild + restart loop

When you change `src/`, ship a new image and roll the revision:

```powershell
$env:PYTHONIOENCODING = 'utf-8'
az acr build -r $env:ACR_NAME -t zava-chat-app:latest --no-logs c:\dev\ai-agents-workshop

$rev = az containerapp show -n zava-chat-app -g $env:AZURE_RESOURCE_GROUP `
  --query "properties.latestRevisionName" -o tsv
az containerapp revision restart -n zava-chat-app -g $env:AZURE_RESOURCE_GROUP --revision $rev
```

Because the Container App pulls `:latest`, restarting the active revision
is enough — no need to bump an image tag.

### 05: Rotate the password

The password lives in the `basic-auth-password` secret. To rotate:

```powershell
az containerapp secret set -n zava-chat-app -g $env:AZURE_RESOURCE_GROUP `
  --secrets "basic-auth-password=<new-password>"

# secrets reload on the next revision
az containerapp update -n zava-chat-app -g $env:AZURE_RESOURCE_GROUP `
  --set-env-vars BASIC_AUTH_PASSWORD=secretref:basic-auth-password
```

## Troubleshooting

| Symptom | Fix |
| ------- | --- |
| Browser keeps prompting for credentials | Most browsers cache Basic auth per-tab. Close all tabs to the FQDN, retry. |
| `GET /` returns 200 but chat says `Error: HTTP 500` | Container logs (`az containerapp logs show -n zava-chat-app -g $RG --follow`) usually show a missing Foundry env var or a role-not-propagated `403`. |
| Dropdown is empty | `/models` is returning `[]` because `ORCHESTRATOR_MODEL_CHOICES` was set to an empty string. Re-set it with a valid CSV. |
| `model 'gpt-X' is not in allowed list` 400 | Add the deployment name to `ORCHESTRATOR_MODEL_CHOICES` and update. |

## Next

The app is live. When you finish the demo, continue to
[Exercise 12 — Resource Cleanup](../12_cleanup/12_cleanup.md) and follow
the new step that deletes `zava-chat-app`.

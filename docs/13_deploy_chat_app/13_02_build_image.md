---
title: '2. Build the image with ACR Tasks'
layout: default
nav_order: 2
parent: 'Exercise 13: Deploy the Chat App to Container Apps'
---

# Task 13.02 — Build the image with `az acr build`

## Introduction

The repo's root [`Dockerfile`](../../Dockerfile) packages the FastAPI app
and runs it under `uvicorn`. There is **no local Docker required** —
`az acr build` ships the source to ACR Tasks and builds it there.

## Success Criteria

{: .success }
> - `az acr repository show -n <acr> --image zava-chat-app:latest` returns
>   a digest you just produced.
> - The build run reports `provisioningState: Succeeded`.

## Key Tasks

### 01: Confirm the Dockerfile and `.dockerignore`

Open [`Dockerfile`](../../Dockerfile) — it is a standard
`python:3.12-slim` image that copies the repo, installs
`requirements.txt`, and runs:

```dockerfile
CMD ["sh", "-c", "uvicorn src.app.main:app --host 0.0.0.0 --port ${PORT:-8000}"]
```

[`.dockerignore`](../../.dockerignore) excludes `.venv`, `docs/`, `.env`,
`__pycache__`, `solution/` — keep it tight so the build context stays
small.

### 02: Hydrate your shell from `.env`

```powershell
Get-Content .env | Where-Object { $_ -and $_ -notmatch '^\s*#' } | ForEach-Object {
    $name, $value = $_ -split '=', 2
    if ($name -and $value) {
        [Environment]::SetEnvironmentVariable($name.Trim(), $value.Trim().Trim('"'), 'Process')
    }
}
$ACR = $env:ACR_NAME
$ACR
```

### 03: Build the image

```powershell
# Workaround for a known colorama / cp1252 crash when streaming build logs
# from Windows PowerShell.
$env:PYTHONIOENCODING = 'utf-8'

az acr build `
  --registry $ACR `
  --image zava-chat-app:latest `
  --no-logs `
  c:\dev\ai-agents-workshop
```

`--no-logs` avoids the UnicodeEncodeError some Windows terminals throw
while ACR streams Docker output. The build still runs to completion in
ACR; you can re-fetch logs any time with:

```powershell
az acr task logs --registry $ACR --run-id <runId>
```

### 04: Verify the image landed

```powershell
az acr repository show `
  -n $ACR --image zava-chat-app:latest `
  --query "{lastUpdate:lastUpdateTime,digest:digest}" -o json
```

## Troubleshooting

| Symptom | Fix |
| ------- | --- |
| `UnicodeEncodeError 'charmap' codec` | Set `$env:PYTHONIOENCODING='utf-8'` **and** pass `--no-logs`. |
| Build context > 10 MB | `.dockerignore` is not excluding `.venv`/`docs/` — re-check it. |
| `Unauthorized` from ACR | Run `az login` and `az account set --subscription <id>`. |

## Next

Continue to [13.03 — Create the Container App](13_03_create_container_app.md).

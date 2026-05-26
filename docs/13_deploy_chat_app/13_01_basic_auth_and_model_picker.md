---
title: '1. Add Basic auth + runtime model picker'
layout: default
nav_order: 1
parent: 'Exercise 13: Deploy the Chat App to Container Apps'
---

# Task 13.01 — Basic auth + runtime model picker

## Introduction

Before pushing anything to Azure, two small features were added to the
chat app so it is safe to expose publicly and easy to demo:

1. **HTTP Basic auth** in front of every interactive route (`/`,
   `/chat`, `/chat/stream`, `/models`). `/health` stays open so Container
   Apps probes still work.
2. A **`/models` endpoint** plus a `<select>` dropdown in the UI so the
   presenter can switch the orchestrator (Magentic *manager*) model per
   request — `gpt-4.1`, `gpt-4.1-mini`, `gpt-4o`, `gpt-4o-mini` — with no
   redeploy.

Hosted Foundry specialists (`store_ops`, `products`, `marketing`,
`response_generator`) keep their own deployments — those are configured
on the Foundry agent definition, not in the container.

## Success Criteria

{: .success }
> - Running `uvicorn src.app.main:app --reload --port 8000` with
>   `BASIC_AUTH_USERNAME` and `BASIC_AUTH_PASSWORD` set requires a
>   browser login.
> - With the env vars unset, the app still works (auth bypassed) — useful
>   for local dev.
> - `GET /models` returns
>   `{"default":"gpt-4.1","choices":["gpt-4.1","gpt-4.1-mini",…]}`.
> - The dropdown next to the input shows those options and the selected
>   value is forwarded as `{"query":…, "model":"gpt-4o-mini"}` to
>   `/chat/stream`.

## Key Tasks

### 01: Review the basic-auth middleware

[`src/app/main.py`](../../src/app/main.py) reads two env vars at startup:

```python
_BASIC_AUTH_USERNAME = os.environ.get("BASIC_AUTH_USERNAME", "")
_BASIC_AUTH_PASSWORD = os.environ.get("BASIC_AUTH_PASSWORD", "")
_BASIC_AUTH_ENABLED  = bool(_BASIC_AUTH_USERNAME and _BASIC_AUTH_PASSWORD)
```

If both are set, `require_basic_auth()` is added as a `Depends(...)` on
every interactive route. It uses `secrets.compare_digest` for constant-
time comparison and returns `WWW-Authenticate: Basic` on failure.

### 02: Review the `/models` endpoint and allowlist

The list of pickable models is read from an env var so you can change it
at deploy-time without rebuilding:

```python
_DEFAULT_MODEL_CHOICES = "gpt-4.1,gpt-4.1-mini,gpt-4o,gpt-4o-mini"
_ALLOWED_MODELS = [
    m.strip()
    for m in os.environ.get("ORCHESTRATOR_MODEL_CHOICES", _DEFAULT_MODEL_CHOICES).split(",")
    if m.strip()
]
```

`_resolve_model()` validates the requested name against `_ALLOWED_MODELS`
and rejects unknown values with HTTP 400 — important so an attacker can
not coax the manager into using an arbitrary deployment.

### 03: Review how the orchestrator accepts the override

[`src/orchestrator/magentic_router.py`](../../src/orchestrator/magentic_router.py)
now takes an optional `manager_model` everywhere a workflow is built:

```python
async def stream_query(user_query, *, manager_model: str | None = None):
    ...
    workflow = build_workflow(cred, manager_model=manager_model)

def build_workflow(credential, *, manager_model: str | None = None):
    ...
    client = FoundryChatClient(
        project_endpoint=settings.azure_ai_project_endpoint,
        model=manager_model or settings.azure_ai_model_deployment,
        credential=credential,
    )
```

When the request body has no `model` field, the workflow falls back to
`AZURE_AI_MODEL_DEPLOYMENT` from `.env` (or the container env var).

### 04: Review the UI dropdown

[`src/app/chat.html`](../../src/app/chat.html) gained:

```html
<select id="model-select"></select>
```

…in the chat-input bar, plus a small loader that calls `/models` and
populates the options on page load. The selected value is included in the
`fetch('/chat/stream', { body: JSON.stringify({ query, model }) })`
call.

## Try it locally

```powershell
$env:BASIC_AUTH_USERNAME = "demo-admin"
$env:BASIC_AUTH_PASSWORD = 'M$FT#AI@2026'   # single quotes — $ is literal
uvicorn src.app.main:app --reload --port 8000
```

* Open <http://127.0.0.1:8000/> — browser prompts for credentials.
* Open DevTools → Network → reload — you should see `GET /models`
  returning JSON.
* Change the dropdown, ask a question, watch the `POST /chat/stream`
  payload include your chosen `model`.

To **turn auth off** for local dev, just don't set the env vars
(or `Remove-Item Env:BASIC_AUTH_PASSWORD`).

## Next

Continue to [13.02 — Build the image](13_02_build_image.md).

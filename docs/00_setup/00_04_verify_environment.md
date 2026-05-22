---
title: '4. Verify your environment'
layout: default
nav_order: 4
parent: 'Exercise 00: Setup & Verify Resources'
---

# Task 00.04 — Run the Smoke Tests and Connectivity Checks

## Steps

1. **Run the offline smoke tests**

   ```powershell
   pytest tests/test_smoke.py -q
   ```

   All seven tests should pass. They confirm the repo layout is correct and
   the seed JSON / Markdown files are well-formed.

2. **Confirm settings load**

   ```powershell
   python -c "from src.common.settings import get_settings; import json; print(json.dumps(get_settings().model_dump(), indent=2))"
   ```

   Every required value should be populated (anything optional may be blank).

3. **Confirm Cosmos DB connectivity**

   ```powershell
   python -c "from src.common.cosmos import get_cosmos_client; print([d['id'] for d in get_cosmos_client().list_databases()])"
   ```

   You should see at least the databases that already exist on the account
   (could be empty `[]` — that's fine, we will create the `pepsico` database
   in Exercise 01).

4. **Confirm Foundry project connectivity**

   ```powershell
   python -c "from src.common.foundry_client import get_project_client; print([m.name for m in get_project_client().agents.list()])"
   ```

   This will return either an empty list (no agents yet — expected) or the
   names of any pre-existing agents. As long as it does **not** raise, you
   are authenticated.

## Troubleshooting

<details markdown="block"><summary><strong>`DefaultAzureCredential failed to retrieve a token`</strong></summary>

Re-run `az login`, ensure the subscription is set, and verify you are not
behind a corporate proxy that blocks `login.microsoftonline.com`.

</details>

<details markdown="block"><summary><strong>`403 Forbidden` from Cosmos DB</strong></summary>

You are missing the **`Cosmos DB Built-in Data Contributor`** role. Ask your
platform admin to run:

```powershell
$accountName = "<cosmos-account>"
$rg          = "<rg>"
$principalId = az ad signed-in-user show --query id -o tsv
az cosmosdb sql role assignment create `
  --account-name $accountName -g $rg `
  --scope "/" `
  --principal-id $principalId `
  --role-definition-id "00000000-0000-0000-0000-000000000002"
```

</details>

<details markdown="block"><summary><strong>The Foundry project endpoint returns 404</strong></summary>

Double-check the **endpoint URL format**. It must be the project endpoint
(`https://<account>.services.ai.azure.com/api/projects/<project>`), not the
account endpoint.

</details>

## Success criteria

{: .success }
> - `pytest tests/test_smoke.py -q` reports `7 passed`
> - The `Settings` JSON dump shows every variable populated
> - The Cosmos DB and Foundry connectivity probes both succeed

## Next

You are ready to start building. Continue to
[Exercise 01 — Scaffold the Chat App](../01_chat_app_scaffold/01_chat_app_scaffold.md).

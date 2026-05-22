---
title: '1. Provision the knowledge base'
layout: default
nav_order: 1
parent: 'Exercise 03: HR Agent (Foundry IQ)'
---

# Task 03.01 — Provision the HR Foundry IQ Knowledge Base

`src/foundry_agents/setup_hr_knowledge_base.py` does the entire pipeline in
one Python script:

1. Creates the Azure AI Search **index** `pepsico-hr-source` if it doesn't exist.
2. Uploads the four markdown files from `src/knowledge_seed/hr/` as searchable documents.
3. Creates the Foundry IQ **knowledge base** `pepsico-hr-kb` pointing at that index.
4. Registers a **Foundry project connection** `pepsico-hr-kb-conn` so the
   agent can reach the KB's MCP endpoint via the project's managed identity.

## Pre-requisites

- `AZURE_SEARCH_ENDPOINT` and `AZURE_AI_PROJECT_RESOURCE_ID` are set in `.env`.
- Your user has `Search Service Contributor` + `Search Index Data Contributor`
  on the Search service.
- The Foundry project's managed identity has `Search Index Data Reader` on the
  Search service. (Ask your platform admin if missing.)

## Steps

1. **Run the setup script**

   ```powershell
   python -m src.foundry_agents.setup_hr_knowledge_base
   ```

   Expected output (tail):

   ```text
   INFO Index 'pepsico-hr-source' ready
   INFO Uploaded 4 HR docs to index 'pepsico-hr-source'
   INFO Knowledge base 'pepsico-hr-kb' ready
   INFO Foundry project connection 'pepsico-hr-kb-conn' -> https://<search>.search.windows.net/knowledgebases/pepsico-hr-kb/mcp?api-version=2025-11-01-preview
   {
     "search_index": "pepsico-hr-source",
     "knowledge_base": "pepsico-hr-kb",
     "project_connection": "pepsico-hr-kb-conn"
   }
   ```

2. **Verify in the Foundry portal**

   - **Management center → Knowledge bases** → confirm `pepsico-hr-kb` exists.
   - **Management center → Connections** → confirm `pepsico-hr-kb-conn` exists
     with type **Remote tool** and **Project managed identity** auth.

3. **Verify the index in the Azure portal**

   - Open the Azure AI Search service → **Indexes → pepsico-hr-source**.
   - Click **Search explorer** and run `*` — you should see 4 documents.

## How the connection authorises retrieval

The Foundry project's **managed identity** holds `Search Index Data Reader`
on your Search service. When the HR agent calls the MCP knowledge base, the
project forwards a token for `https://search.azure.com/` on behalf of the
project identity. That's why we set:

```python
audience="https://search.azure.com/",
auth_type="ProjectManagedIdentity",
```

in `setup_hr_knowledge_base.py`.

## Success criteria

{: .success }
> - The script prints the final JSON dictionary
> - The Foundry portal shows the new KB and connection
> - Azure AI Search Explorer returns 4 documents

## Next

[03.02 — Create the HR Foundry agent](03_02_create_hr_agent.md).

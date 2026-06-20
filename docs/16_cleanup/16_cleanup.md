---
title: 'Exercise 16: Clean Up'
layout: default
nav_order: 2
parent: 'Module 7: Governance & Wrap-Up'
has_children: false
---

# Exercise 16 — Clean Up Azure Resources

## Why clean up

Azure resources (Foundry, Azure AI Search, Container Apps, Cosmos DB,
Application Insights) were **pre-provisioned** for the workshop. To avoid
ongoing charges, remove the things **you created** during the exercises —
without deleting the shared, pre-provisioned account itself.

## Steps

### 1. Delete the Container Apps you deployed

```powershell
foreach ($appName in 'zava-chat-app','zava-sales-mcp','zava-inventory-mcp','zava-marketing-mcp') {
    az containerapp delete --name $appName `
      --resource-group $env:AZURE_RESOURCE_GROUP --yes 2>$null
}
```

(Adjust the names to whatever you used when deploying the MCP servers and
chat app.)

### 2. (Optional) Remove the Foundry agents and connections you created

In the Foundry portal, delete the agents `zava-sales-agent`,
`zava-inventory-agent`, `zava-marketing-agent`, `zava-intent-detector`,
`zava-action-agent`, `zava-response-generator`, their MCP connections, and the
`zava-marketing-kb` knowledge base if you no longer need them.

### 3. (Optional) Drop the seeded Cosmos data

If the Cosmos account is yours to clean, delete the `zava` database (or its
`sales`, `inventory`, and `marketing_campaigns` containers).

## Success criteria

- The Container Apps you created no longer appear in your resource group.
- No unexpected workshop resources continue to incur cost.

{: .warning }
> Deletes are permanent. Only remove resources you created — do **not** delete
> the shared, pre-provisioned account or resource group unless you own it.

## References

- [Delete a resource group](https://learn.microsoft.com/azure/azure-resource-manager/management/delete-resource-group)
- [`az containerapp delete`](https://learn.microsoft.com/cli/azure/containerapp#az-containerapp-delete)

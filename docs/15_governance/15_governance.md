---
title: 'Exercise 15: Governance'
layout: default
nav_order: 1
parent: 'Module 7: Governance & Wrap-Up'
has_children: false
---

# Exercise 15 — Govern the Multi-Agent System

## Scenario

You now have a complete, deployed, evaluated, and observable multi-agent
assistant. Before it touches real store managers, the platform team needs to
answer a different set of questions: *Who is allowed to use it? What is it
allowed to say and do? How much will it cost? Can we prove it behaves?*

This exercise is a **concept walkthrough** — there is no new code to write. It
maps the governance controls you should have in place to the Azure services the
workshop already uses.

---

## 1. Identity & access (RBAC)

Every component authenticates with **Microsoft Entra ID** — there are no API
keys in the codebase.

- **Managed identities** — the Container Apps (chat app and MCP servers) and the
  Foundry agents use managed identities, not secrets, to reach Cosmos DB, Azure
  AI Search, and the Foundry project.
- **Least privilege** — grant each identity only the roles it needs (for
  example, `Cosmos DB Built-in Data Reader` for read-only tools).
- **Human access** — workshop participants get scoped roles on the shared
  Foundry project rather than subscription-wide ownership.

> Review the role assignments on your resource group: every assignment should
> trace to a specific component or person and a clear reason.

---

## 2. Content safety & responsible AI

Guardrails (Module 6) stop bad inputs and outputs at runtime; governance is the
**policy** behind them.

- **Azure AI Content Safety** — configure severity thresholds for hate, sexual,
  violence, and self-harm categories on model deployments.
- **System-prompt policy** — each agent's instructions define what it must
  refuse and how it must cite data. Keep these under version control so changes
  are reviewable.
- **Human-in-the-loop** — the Action Recommender *suggests*; a person approves
  store changes. Decide which actions may ever be fully automated.

---

## 3. Cost governance

A multi-agent system multiplies model calls — one user turn can fan out to
several agents.

- **Budgets & alerts** — set Azure Cost Management budgets on the resource group
  and alert when spend crosses a threshold.
- **Model right-sizing** — use smaller, cheaper deployments for routing/intent
  and reserve larger models for synthesis.
- **Token controls** — cap context size and tool-result payloads; the MCP tools
  return compact JSON for exactly this reason.
- **Quotas** — set per-deployment rate limits so a runaway loop cannot exhaust
  capacity for everyone.

---

## 4. Compliance & auditability

- **Tracing as evidence** — the OpenTelemetry traces from
  [Exercise 13](../13_observability/13_observability.md) are your audit trail:
  every agent hop, tool call, and model response is recorded.
- **Continuous evaluation** — the scheduled evaluations from
  [Exercise 12](../12_evaluations/12_evaluations.md) provide ongoing evidence
  that quality has not regressed.
- **Data residency & retention** — confirm Cosmos DB, Azure AI Search, and
  Application Insights live in approved regions with retention policies that
  match your compliance requirements.

---

## Success criteria

{: .success }
> By the end of this exercise you can:
> - Explain how each component authenticates without secrets.
> - Point to where content-safety policy is enforced for the assistant.
> - Describe two ways to keep model costs predictable.
> - Identify which telemetry serves as the audit trail.

## Reflection

Governance is not a final gate — it is the operating model that lets you keep
shipping. Revisit identity, safety, cost, and compliance every time you add an
agent or a tool.

## References

- [Responsible use of AI in Foundry](https://learn.microsoft.com/azure/ai-foundry/responsible-use-of-ai-overview)
- [Managed identities for Azure resources](https://learn.microsoft.com/entra/identity/managed-identities-azure-resources/overview)
- [Azure AI Content Safety overview](https://learn.microsoft.com/azure/ai-services/content-safety/overview)

## Next

Continue to
[Exercise 16 — Clean Up Azure Resources](../16_cleanup/16_cleanup.md) to remove
the resources you created during the workshop.

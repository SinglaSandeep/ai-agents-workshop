---
title: 'Exercise 10: Guardrails & Red Teaming'
layout: default
nav_order: 12
has_children: true
---

# Exercise 10 — Guardrails and Red Teaming the Marketing Agent

## Scenario

Microsoft Foundry already applies model-side content safety to every Prompt
Agent, but production deployments need explicit guardrails and adversarial
testing. We'll:

1. Confirm Foundry's default **content safety** is doing its job for the
   Marketing agent (no Python middleware needed for Prompt Agents).
2. Author **custom shared policies** in the Foundry portal (a "no medical
   advice" + "no comparison vs competitor by name" policy) and attach them
   to the Marketing agent.
3. Run an **automated red-team scan** against the registered Marketing
   Prompt Agent using `azure-ai-evaluation[redteam]` to probe for violence,
   hate, sexual, and self-harm risk categories with several attack
   strategies.

## Description

You will:

1. Verify Foundry content safety on the Marketing agent in the Playground.
2. Create a shared custom policy in Foundry and attach it to the Marketing
   agent.
3. Implement `red_team/red_team_scan_local.py` and run an automated
   red-team scan against the registered Prompt Agent.

## Success Criteria

{: .success }
> - The Marketing agent returns a friendly refusal for an obviously
>   disallowed prompt in the Foundry Playground.
> - At least one custom policy is attached to `zava-marketing-agent` in
>   the Foundry portal.
> - `python -m src.red_team.red_team_scan_local` produces a results
>   JSON with non-zero pass counts in all four risk categories.

## Learning Resources

* [Cloud-based red teaming](https://learn.microsoft.com/azure/foundry/how-to/develop/run-ai-red-teaming-cloud)
* [Foundry content safety](https://learn.microsoft.com/azure/ai-foundry/responsible-ai/content-safety)
* [Custom shared policies for agents](https://learn.microsoft.com/azure/ai-foundry/agents/policies)

## Tasks

| Task | Description |
| ---- | ----------- |
| [10.01 — Foundry content safety on a Prompt Agent](10_01_guardrails_middleware.md) | Confirm built-in content safety and refusal behaviour. |
| [10.02 — Author shared custom policies](10_02_custom_policies.md) | Create and attach a "no medical advice" policy. |
| [10.03 — Run an automated red-team scan](10_03_red_team_scan.md) | Implement and run the local red-team script. |

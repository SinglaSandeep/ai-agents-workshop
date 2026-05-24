---
title: 'Exercise 10: Guardrails & Red Teaming'
layout: default
nav_order: 12
has_children: true
---

# Exercise 10 — Guardrails and Red Teaming the Marketing Agent

## Scenario

Hosting the Marketing agent on Foundry gives us several safety layers for
free, but production agents need explicit guardrails and adversarial testing.
We'll:

1. Add a **content-filter middleware** to the hosted agent so model-side
   content-safety blocks produce a clean refusal rather than a stack trace.
2. Author **custom shared policies** in the Foundry portal (a "no medical
   advice" + "no comparison vs competitor by name" policy).
3. Run an **automated red-team scan** against the locally running hosted
   agent using `azure-ai-evaluation[redteam]` to probe for violence, hate,
   sexual, and self-harm risk categories with several attack strategies.

> Adapted from
> [Azure-Samples/foundry-hosted-agentframework-demos](https://github.com/Azure-Samples/foundry-hosted-agentframework-demos)
> (`agents/stage4_foundry_hosted.py` middleware, `scripts/red_team_scan_local.py`).

## Description

You will:

1. Drop a `content_filter_middleware` into the Marketing hosted agent and
   redeploy.
2. Create a shared custom policy in Foundry and attach it to the Marketing
   agent.
3. Implement `red_team/red_team_scan_local.py` and run an automated
   red-team scan against the local agent.

## Success Criteria

{: .success }
> - The hosted Marketing agent returns a friendly refusal for content-filter
>   blocks rather than an HTTP 500.
> - At least one custom policy is attached to `zava-marketing-agent` in
>   the Foundry portal.
> - `python -m solution.red_team.red_team_scan_local` produces a results
>   JSON with non-zero pass counts in all four risk categories.

## Learning Resources

* [Cloud-based red teaming](https://learn.microsoft.com/azure/foundry/how-to/develop/run-ai-red-teaming-cloud)
* [Foundry content safety](https://learn.microsoft.com/azure/ai-foundry/responsible-ai/content-safety)
* [Custom shared policies for agents](https://learn.microsoft.com/azure/ai-foundry/agents/policies)

## Tasks

| Task | Description |
| ---- | ----------- |
| [10.01 — Add the content-filter middleware](10_01_guardrails_middleware.md) | Wrap the agent with a friendly refusal middleware. |
| [10.02 — Author shared custom policies](10_02_custom_policies.md) | Create and attach a "no medical advice" policy. |
| [10.03 — Run an automated red-team scan](10_03_red_team_scan.md) | Implement and run the local red-team script. |

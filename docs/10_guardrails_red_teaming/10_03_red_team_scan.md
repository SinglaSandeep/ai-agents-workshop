---
title: '3. Automated red-team scan'
layout: default
nav_order: 3
parent: 'Exercise 10: Guardrails & Red Teaming'
---

# Task 10.03 — Run an Automated Red-Team Scan

## Introduction

`azure-ai-evaluation[redteam]` ships a `RedTeam` orchestrator that generates
adversarial prompts across configurable risk categories and attack strategies
and replays them against a callback target. We'll run it against the
**locally running** hosted Marketing agent (`azd ai agent run`).

> Hosted-cloud red teaming for hosted agents is not yet GA for this scenario.
> Use the local flow for now; once cloud support lands, the same script can
> point at the deployed `/responses` endpoint.

## Success Criteria

* `python -m solution.red_team.red_team_scan_local` writes a results JSON.
* The rendered summary shows non-zero passed counts in all four risk
  categories.

## Key Tasks

### 01: Run the local hosted agent

```powershell
cd src/foundry_agents/marketing_hosted
azd ai agent run
```

Leave this running. It exposes `http://localhost:8088/responses`.

### 02: Implement `red_team/red_team_scan_local.py`

Open [src/red_team/red_team_scan_local.py](../../src/red_team/red_team_scan_local.py).

<details markdown="block">
<summary><strong>Expand for the solution</strong></summary>

See [solution/red_team/red_team_scan_local.py](../../solution/red_team/red_team_scan_local.py).
It builds a `RedTeam` configured with `Violence`, `HateUnfairness`, `Sexual`
and `SelfHarm` risk categories and the `Baseline`, `Url`, and `Tense` attack
strategies, invokes the agent over local HTTP, and prints a rich summary.

</details>

### 03: Run the scan

In a second terminal:

```powershell
python -m solution.red_team.red_team_scan_local
```

Expected: a `red_team_output/local_redteam_output_<timestamp>/` directory
containing `results.json`, plus a console table.

### 04: Show previous results

```powershell
python -m solution.red_team.red_team_scan_local --show-results
```

## Next

Continue to [Exercise 11 — Observability](../11_observability/11_observability.md).

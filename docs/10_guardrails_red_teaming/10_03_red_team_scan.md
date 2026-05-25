---
title: '3. Automated red-team scan'
layout: default
nav_order: 3
parent: 'Exercise 10: Guardrails & Red Teaming'
---

# Task 10.03 — Run an Automated Red-Team Scan

## Introduction

`azure-ai-evaluation[redteam]` ships a `RedTeam` orchestrator that generates
adversarial prompts across configurable risk categories and attack
strategies and replays them against a callback target. We'll point it at the
registered Marketing Foundry Prompt Agent.

## Success Criteria

* `python -m src.red_team.red_team_scan_local` writes a results JSON.
* The rendered summary shows non-zero passed counts in all four risk
  categories.

## Key Tasks

### 01: Make sure the agent is registered

```powershell
python -m src.foundry_agents.create_marketing_agent
```

(Skip if you already did this in Exercise 05.)

### 02: Implement `red_team/red_team_scan_local.py`

Open [src/red_team/red_team_scan_local.py](https://github.com/SinglaSandeep/ai-agents-workshop/blob/main/src/red_team/red_team_scan_local.py).


### 03: Run the scan

```powershell
python -m src.red_team.red_team_scan_local
```

Expected: a `red_team_output/local_redteam_output_<timestamp>/` directory
containing `results.json`, plus a console table.

### 04: Show previous results

```powershell
python -m src.red_team.red_team_scan_local --show-results
```

## Next

Continue to [Exercise 11 — Observability](../11_observability/11_observability.md).

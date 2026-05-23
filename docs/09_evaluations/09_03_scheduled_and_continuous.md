---
title: '3. Scheduled & continuous evaluation'
layout: default
nav_order: 3
parent: 'Exercise 09: Evaluations'
---

# Task 09.03 — Schedule Daily and Continuous Evaluation

## Introduction

Two layered patterns:

1. **Scheduled evaluation** — re-runs the ground-truth dataset on a cadence
   (e.g. daily) so regressions show up before users complain.
2. **Continuous evaluation** — samples a fraction of live agent traces and
   scores them against a subset of evaluators (typically task adherence,
   groundedness, relevance). Great for catching drift in production.

## Success Criteria

* A daily schedule named `marketing-quality-daily` exists.
* A continuous evaluation named `marketing-continuous` is active.
* (Optional) An Azure Monitor alert fires if the pass rate falls below your
  threshold.

## Key Tasks

### 01: Register the daily quality schedule

```powershell
python -m solution.evaluations.scheduled_eval
```

What it does: creates a daily-cadence schedule that re-runs `quality_eval.py`'s
evaluation definition against the latest agent version.

### 02: Enable continuous evaluation

```powershell
python -m solution.evaluations.continuous_eval
```

What it does: creates a continuous-evaluation rule that samples ~10% of live
agent traces and scores them with Task Adherence, Groundedness, and
Relevance evaluators. Results stream into Application Insights.

### 03: (Optional) Wire an alert

```powershell
python -m solution.evaluations.continuous_eval_alert
```

Creates an Azure Monitor metric alert that fires when the rolling
continuous-eval pass rate drops under 80% for 30 minutes.

### 04: Verify in the Foundry portal

* **Observability → Evaluations → Schedules** lists `marketing-quality-daily`.
* **Observability → Evaluations → Continuous** lists `marketing-continuous`.
* **Application Insights → Alerts** lists the rule (if you ran step 03).

## Next

Continue to [Exercise 10 — Guardrails + Red Teaming](../10_guardrails_red_teaming/10_guardrails_red_teaming.md).

---
title: 'Exercise 09: Evaluations'
layout: default
nav_order: 11
has_children: true
---

# Exercise 09 — Quality Evaluations on the Hosted Marketing Agent

## Scenario

Now that the Marketing agent is hosted on Foundry (Exercise 05), we can lean
on Foundry's built-in evaluators to check **task adherence**, **tool selection**,
**groundedness**, and other quality dimensions on a ground-truth dataset.
Once we trust the bulk evaluation flow, we'll schedule it to run on a cadence
and turn on **continuous evaluation** to sample a fraction of live agent
traces for ongoing quality monitoring.

> Adapted from
> [Azure-Samples/foundry-hosted-agentframework-demos](https://github.com/Azure-Samples/foundry-hosted-agentframework-demos)
> (`scripts/quality_eval.py`, `scheduled_eval.py`, `continuous_eval.py`).

## Description

You will:

1. Curate a small ground-truth dataset (`eval_data/quality_ground_truth.jsonl`)
   for the Marketing agent.
2. Implement and run `evaluations/quality_eval.py` against the latest hosted
   agent version. It uploads the dataset, creates an evaluation, executes a
   run, and saves the per-item output.
3. Use `evaluations/scheduled_eval.py` to register a **daily** quality eval.
4. Use `evaluations/continuous_eval.py` to enable hourly continuous evaluation
   against a sample of live agent traces.
5. (Optional) Use `evaluations/continuous_eval_alert.py` to wire an Azure
   Monitor alert on the pass-rate metric.

## Success Criteria

{: .success }
> - `python -m solution.evaluations.quality_eval` produces a `completed` run
>   and writes `eval_output/quality_eval_output_zava-marketing-agent.json`.
> - A scheduled quality evaluation appears in the Foundry portal under
>   **Observability → Evaluations → Schedules**.
> - A continuous evaluation is active and starts emitting per-trace results.

## Learning Resources

* [Evaluate AI agents in Foundry](https://learn.microsoft.com/azure/foundry/observability/how-to/evaluate-agent)
* [Continuous evaluation overview](https://learn.microsoft.com/azure/foundry/observability/how-to/continuous-evaluation)
* [Region support for evaluations](https://learn.microsoft.com/azure/foundry/concepts/evaluation-regions-limits-virtual-network)

## Tasks

| Task | Description |
| ---- | ----------- |
| [09.01 — Curate the ground-truth dataset](09_01_ground_truth_dataset.md) | Author `quality_ground_truth.jsonl`. |
| [09.02 — Run a one-shot quality evaluation](09_02_quality_eval.md) | Implement and run `quality_eval.py`. |
| [09.03 — Schedule daily + continuous evaluation](09_03_scheduled_and_continuous.md) | Register schedules and (optionally) an alert. |

---
title: '2. Quality evaluation'
layout: default
nav_order: 2
parent: 'Exercise 09: Evaluations'
---

# Task 09.02 — Run a One-Shot Quality Evaluation

## Introduction

The script:

1. Looks up the latest version of `pepsico-marketing-agent`.
2. Uploads the ground-truth dataset to Foundry.
3. Creates an evaluation with the built-in evaluators (Task Adherence, Tool
   Selection, Tool Call Accuracy, Intent Resolution, Groundedness,
   Relevance, Response Completeness).
4. Runs the evaluation against the agent.
5. Polls until it completes and saves per-item output to `eval_output/`.

## Success Criteria

* The eval run reaches status `completed`.
* `eval_output/quality_eval_output_pepsico-marketing-agent.json` is written.
* The run is visible in the Foundry portal under
  **Observability → Evaluations**.

## Key Tasks

### 01: Implement `evaluations/quality_eval.py`

Open [src/evaluations/quality_eval.py](https://github.com/SinglaSandeep/ai-agents-workshop/blob/main/src/evaluations/quality_eval.py).

<details markdown="block">
<summary><strong>Expand to view the full solution</strong></summary>

See [solution/evaluations/quality_eval.py](https://github.com/SinglaSandeep/ai-agents-workshop/blob/main/solution/evaluations/quality_eval.py).
It is a near-direct port of the sample-repo script, retargeted at
`pepsico-marketing-agent` and the three tools we wired in Exercise 05.

</details>

### 02: Run it

```powershell
python -m solution.evaluations.quality_eval
```

Expected console:

```
Agent: pepsico-marketing-agent  version: 3
Uploaded dataset: ds-...
Created evaluation: eval-...
Evaluation run started: run-...  status: queued
Polling for completion...
Run finished — status: completed
Report URL: https://ai.azure.com/...
Output items (8) saved to eval_output/quality_eval_output_pepsico-marketing-agent.json
```

### 03: Inspect the report

Open the **Report URL** from the console. You'll see per-evaluator pass rates
and per-item drill-down with the agent's response, expected response, and
score reasoning.

## Next

Continue to [09.03 — Schedule daily + continuous evaluation](09_03_scheduled_and_continuous.md).

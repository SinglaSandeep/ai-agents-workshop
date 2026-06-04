---
title: '1. Ground-truth dataset'
layout: default
nav_order: 1
parent: 'Exercise 09: Evaluations'
---

# Task 09.01 — Curate the Ground-Truth Dataset

## Introduction

Foundry quality evaluation needs a JSONL dataset. Each row carries a `query`
the agent should be able to answer and a `ground_truth` reference answer.
Evaluators like `response_completeness` and `groundedness` use that reference
to score the agent's output.

## Success Criteria

* `evaluations/eval_data/quality_ground_truth.jsonl` exists with at least
  six representative Marketing prompts and gold answers.

## Key Tasks

### 01: Use the starter dataset

We ship a starter at
[src/evaluations/eval_data/quality_ground_truth.jsonl](https://github.com/SinglaSandeep/ai-agents-workshop/blob/main/src/evaluations/eval_data/quality_ground_truth.jsonl).
Copy it into `src/` for your run, then add 2-3 of your own prompts.

Each line is:

```json
{"query": "What is the ROI of CMP-2026-001?",
 "ground_truth": "Spring Paint Sale 2026 campaign with budget USD 18M, target +12% aided awareness in DIY homeowners 25-54."}
```

### 02: Cover the three tool surfaces

Make sure the dataset exercises all three Marketing tools:

| Tool | Example prompt |
| ---- | -------------- |
| `marketing_mcp` (Cosmos) | *"What is the budget of CMP-2026-002?"* |
| `marketing_kb` (Foundry IQ) | *"What worked and what did not in the 2025 SuperBowl post-mortem?"* |
| `toolbox.web_search` | *"What are the latest national paint price trends?"* |

## Next

Continue to [09.02 — Run a one-shot quality evaluation](09_02_quality_eval.md).

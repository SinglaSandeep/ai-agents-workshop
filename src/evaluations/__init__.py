"""Evaluation and guardrail scripts for the Zava Foundry agents.

This package contains the cloud-based Microsoft Foundry evaluation flows used in
Module 6 (Evaluate, Trace & Guardrails):

* ``sales_quality_eval`` — runs the top-3 agent evaluators (Intent Resolution,
  Tool Call Accuracy, Task Adherence) against the deployed Sales agent.
* ``sales_red_team`` — runs an AI Red Teaming scan with built-in safety
  evaluators (guardrails exercise).

Both flows target the **deployed** Foundry agent (no local agent run) and
publish their results to the Foundry **Evaluations** tab so you can inspect the
pass/fail reasoning in the portal.
"""

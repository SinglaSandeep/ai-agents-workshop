---
title: '2. Wire into the orchestrator'
layout: default
nav_order: 2
parent: 'Exercise 07: Response Generator'
---

# Task 07.02 — Wire the Response Generator into the Orchestrator

The orchestrator was already coded with the response generator as a
participant (see Exercise 06). Now that the agent actually exists in Foundry,
the manager will start calling it.

## Steps

1. **Re-run the orchestrator on the same queries as Exercise 06**

   ```powershell
   python -m src.orchestrator.runner --query "What is the PTO carryover policy?"
   python -m src.orchestrator.runner --query "Which Gatorade SKUs do we sell, and which active campaigns promote them?"
   ```

2. **Confirm the final answer is now formatted**

   The reply should now look like:

   ```text
   Pepsico's PTO policy lets you carry over up to 5 unused days into the next year.

   - Carryover cap: 5 days.
   - Excess unused PTO is forfeited on December 31.
   - Upon separation, accrued but unused PTO is paid out per local law.

   Sources: hr (pepsico_pto_policy.md)
   ```

3. **Confirm the plan ends with `response_generator`**

   The JSON `--json` output should always finish with `response_generator` as
   the last entry in `plan`.

## Tuning the response

The single most effective lever is the **instructions** in
`create_response_agent.py`. To experiment:

1. Edit the `INSTRUCTIONS` string (tone, length, citation format, etc.).
2. Re-run `python -m src.foundry_agents.create_response_agent` — this
   creates a **new version** of the same agent.
3. Re-run the orchestrator. Foundry resolves the latest version automatically.

## Success criteria

{: .success }
> - Final answers follow the documented structure (lead sentence + body +
>   `Sources:` line)
> - The plan ends with `response_generator`
> - Editing the response agent's instructions changes the output without
>   touching the orchestrator code

## Next

[Exercise 08 — Wire the Chat App & Add Observability](../08_chat_app_and_observability/08_chat_app_and_observability.md).

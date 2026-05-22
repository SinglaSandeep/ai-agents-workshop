---
title: '3. Run the orchestrator from the CLI'
layout: default
nav_order: 3
parent: 'Exercise 06: Magentic Orchestrator'
---

# Task 06.03 — Run the Orchestrator

The Response Generator (Exercise 07) does not exist yet. You can still run
the orchestrator now — the framework will fall back to the last specialist
transcript. After Exercise 07 the final answer will come from the response
generator.

## Steps

1. **Single-domain query (HR)**

   ```powershell
   python -m src.orchestrator.runner --query "What is the PTO carryover policy?"
   ```

   Expected plan: `hr -> response_generator`.

2. **Single-domain query (Products)**

   ```powershell
   python -m src.orchestrator.runner --query "List all our beverages under 200 calories."
   ```

   Expected plan: `products -> response_generator`.

3. **Single-domain query (Marketing + Bing)**

   ```powershell
   python -m src.orchestrator.runner --query "What's the latest news about Doritos Super Bowl ads?"
   ```

   Expected plan: `marketing -> response_generator`. The marketing agent will
   internally call Bing.

4. **Cross-domain query (Products + Marketing)**

   ```powershell
   python -m src.orchestrator.runner --query "Which Gatorade SKUs do we sell, and which active campaigns promote them?"
   ```

   Expected plan: `products -> marketing -> response_generator` (or
   `marketing -> products -> response_generator`).

5. **JSON mode** — full transcripts and events

   ```powershell
   python -m src.orchestrator.runner --query "Which Gatorade SKUs do we sell, and which active campaigns promote them?" --json | Out-File -Encoding utf8 last_run.json
   ```

   Inspect `last_run.json` and look at:
   - `plan` — the order in which specialists were called.
   - `transcripts` — what each specialist returned.
   - `events` — the manager's ledger transitions.

## Troubleshooting

<details markdown="block"><summary><strong>The manager keeps looping on the same specialist</strong></summary>

Your participant `description` strings are probably too similar. Make them
more discriminating, then `python -m src.foundry_agents.create_hr_agent`
(etc.) to recreate the agents — though for the *manager* the descriptions
are set in `magentic_router.py`, so re-run the orchestrator after editing.

</details>

<details markdown="block"><summary><strong>"ResourceNotFound: agent reference not found"</strong></summary>

You haven't created one of the Foundry agents yet. Re-run the appropriate
`create_*_agent.py` from Exercises 03-05.

</details>

## Success criteria

{: .success }
> - Each of the four test queries returns a coherent final answer
> - The cross-domain query calls **two** specialists before the response generator
> - The JSON output's `events` list contains entries for `PLAN_CREATED`,
>   `PROGRESS_LEDGER_UPDATED`, and `TASK_COMPLETED`

## Next

[Exercise 07 — Add the Response Generator Agent](../07_response_generator_agent/07_response_generator_agent.md).

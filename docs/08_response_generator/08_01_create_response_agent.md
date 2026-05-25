---
title: '1. Create the Response Generator agent'
layout: default
nav_order: 1
parent: 'Exercise 08: Response Generator'
---

# Task 08.01 — Create the Response Generator Agent

## Introduction

The Response Generator is a **tools-free** Prompt Agent. The orchestrator
hands it the user's original question plus the specialist transcripts; the
agent produces one polished reply in Zava voice.

## Success Criteria

* `python -m src.foundry_agents.create_response_agent` succeeds.
* `zava-response-generator` shows up in the Foundry portal with zero tools.

## Key Tasks

### 01: Implement `main()`

Open [src/foundry_agents/create_response_agent.py](https://github.com/SinglaSandeep/ai-agents-workshop/blob/main/src/foundry_agents/create_response_agent.py).


### 02: Run it

```powershell
python -m src.foundry_agents.create_response_agent
```

## Next

Continue to [08.02 — Verify the orchestrator hand-off](08_02_wire_into_orchestrator.md).

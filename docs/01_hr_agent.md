---
title: 'Exercise 01: Build the HR Agent'
layout: default
nav_order: 2
parent: Workshop Guide
---

# Exercise 01: Build the HR Agent

## Goal

Create the first specialist agent and validate that it can answer HR questions from a local knowledge source.

## What You Build

- `app/knowledge/hr.md` as the HR knowledge source
- `app/agents/hr.py` as the HR agent factory
- A direct CLI path to call the HR agent

## Steps

1. Review `app/knowledge/hr.md` and identify the sections available to the agent.
2. Review `app/agents/hr.py` and confirm the HR keywords match the knowledge source.
3. Run the HR agent directly.

```bash
python -m app.cli --agent hr --query "What is the PTO policy?"
```

4. Try another HR question.

```bash
python -m app.cli --agent hr --query "Can employees work remotely?"
```

## Success Criteria

- The route is `hr`.
- The answer includes details from the HR knowledge file.
- The response includes at least one source reference.
- You can add a new HR policy paragraph and see it used in a future answer.

## Running Version

The app runs as a single-agent HR assistant from the CLI.

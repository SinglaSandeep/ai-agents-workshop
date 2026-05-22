---
title: 'Exercise 04: Add the Orchestrator'
layout: default
nav_order: 5
parent: Workshop Guide
---

# Exercise 04: Add the Orchestrator

## Goal

Add a routing layer that evaluates each question and sends it to the best specialist agent.

## What You Build

- `app/agents/orchestrator.py` as the routing layer
- Auto-routing in `app/cli.py`
- A small FastAPI app in `app/main.py`

## Steps

1. Review `LocalOrchestrator.route()` and identify how each agent is scored.
2. Run an HR question without choosing an agent.

```bash
python -m app.cli --query "What is the PTO policy?"
```

3. Run a product question without choosing an agent.

```bash
python -m app.cli --query "How much is the fitness watch?"
```

4. Start the web app.

```bash
uvicorn app.main:app --reload --port 8000
```

5. Open http://127.0.0.1:8000 and ask one question for each business domain.

## Success Criteria

- Auto-routing sends HR questions to `hr`.
- Auto-routing sends catalog or pricing questions to `products`.
- Auto-routing sends campaign or brand questions to `marketing`.
- The `/health`, `/agents`, and `/chat` endpoints respond locally.

## Running Version

The app now runs as a local multi-agent assistant with a browser UI and JSON API.

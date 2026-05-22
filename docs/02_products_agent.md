---
title: 'Exercise 02: Add the Products Agent'
layout: default
nav_order: 3
parent: Workshop Guide
---

# Exercise 02: Add the Products Agent

## Goal

Extend the application with a second specialist that answers product catalog and pricing questions.

## What You Build

- `app/knowledge/products.md` as the Products knowledge source
- `app/agents/products.py` as the Products agent factory
- A direct CLI path to call the Products agent

## Steps

1. Review `app/knowledge/products.md` and note the catalog entries.
2. Review `app/agents/products.py` and confirm it includes product-specific routing keywords.
3. Run the Products agent directly.

```bash
python -m app.cli --agent products --query "Tell me about the fitness watch"
```

4. Ask about warranty or price.

```bash
python -m app.cli --agent products --query "What warranty is included with Zava devices?"
```

## Success Criteria

- The route is `products`.
- The answer uses product catalog or warranty details.
- Pricing questions return a price from the local product knowledge file.
- The HR agent still runs after adding the Products agent.

## Running Version

The app now has two independently runnable agents: HR and Products.

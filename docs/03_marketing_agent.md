---
title: 'Exercise 03: Add the Marketing Agent'
layout: default
nav_order: 4
parent: Workshop Guide
---

# Exercise 03: Add the Marketing Agent

## Goal

Add the Marketing specialist so the app can answer campaign, brand, audience, and channel questions.

## What You Build

- `app/knowledge/marketing.md` as the Marketing knowledge source
- `app/agents/marketing.py` as the Marketing agent factory
- A direct CLI path to call the Marketing agent

## Steps

1. Review `app/knowledge/marketing.md` and identify campaign and brand voice guidance.
2. Review `app/agents/marketing.py` and confirm the routing keywords match marketing intent.
3. Run the Marketing agent directly.

```bash
python -m app.cli --agent marketing --query "What campaigns are active?"
```

4. Ask about brand voice.

```bash
python -m app.cli --agent marketing --query "What brand voice should our copy use?"
```

## Success Criteria

- The route is `marketing`.
- Campaign questions return the Spring Wellness campaign.
- Brand questions return tone guidance from the local knowledge file.
- HR and Products direct calls still work.

## Running Version

The app now has three independently runnable specialist agents.

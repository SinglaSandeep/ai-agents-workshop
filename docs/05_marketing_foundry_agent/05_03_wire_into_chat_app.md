---
title: '3. Wire the agent into the chat UI'
layout: default
nav_order: 3
parent: 'Exercise 05: Marketing Foundry Agent (+ Bing)'
---

# Task 05.03 — Wire the Marketing Agent Into the Chat UI

## Introduction

You already implemented `run_single_agent` in Exercise 03 — it dispatches by
`mode`. You only need to flip `AGENT_MODE=marketing` and restart uvicorn.

## Success Criteria

* With `AGENT_MODE=marketing`, the chat UI answers both campaign-data and
  live-web questions.

## Key Tasks

### 01: Flip the mode

Edit `.env`:

```
AGENT_MODE=marketing
```

Restart uvicorn.

### 02: Test in the browser

| Prompt | Expected behaviour |
| ------ | ------------------ |
| *"What active Gatorade campaigns target youth athletes?"* | Uses `list_active_campaigns` / `list_campaigns_by_brand` from MCP. |
| *"What is the ROI of CMP-2026-001?"* | Uses `campaign_performance` from MCP. |
| *"Any news on Pepsi's most recent SuperBowl sponsorship?"* | Uses Bing Grounding; cites URLs. |
| *"What is our PTO policy?"* | Should politely defer — this agent has no HR data. |

The plan pill underneath each answer should say `marketing`.

## Next

Continue to [Exercise 06 — Create the HR Foundry IQ Agent](../06_hr_foundry_iq_agent/06_hr_foundry_iq_agent.md).

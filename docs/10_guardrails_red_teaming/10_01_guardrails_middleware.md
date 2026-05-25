---
title: '1. Content safety overview'
layout: default
nav_order: 1
parent: 'Exercise 10: Guardrails & Red Teaming'
---

# Task 10.01 — Foundry Content Safety on a Prompt Agent

## Introduction

Microsoft Foundry applies model-side **content safety** to every Prompt
Agent automatically: prompts and completions are screened across the
*violence*, *hate*, *sexual* and *self-harm* categories, and disallowed
content is blocked with a clean refusal — no custom middleware required.

This is a major simplification over the hosted-agent path, where you had to
wrap your agent in a Python middleware (`OpenAIContentFilterException` →
friendly refusal) to keep blocked content from becoming an HTTP 500.

## Success Criteria

* You can demonstrate, in the Foundry Playground, that the Marketing agent
  produces a clean refusal for an obviously disallowed prompt.

## Key Tasks

### 01: Confirm content-safety is on

Foundry portal → **Agents → zava-marketing-agent → Configuration**. Under
the model deployment you'll see the active **content filter** profile (the
default `Standard` filter is applied unless you opt in to a custom one).

### 02: Trigger a refusal in the Playground

Foundry portal → **Agents → zava-marketing-agent → Playground**. Send a
clearly disallowed prompt (e.g., a request to draft instructions for
self-harm). The agent should respond with a short refusal rather than an
error.

### 03: (Optional) Tighten the filter

If your tenant policy requires a stricter filter, create a custom
content-filter profile in the Foundry portal (**Content filters → + New**)
and attach it to your model deployment. Re-test in the Playground.

> **Why no Python middleware here?** Prompt Agents run server-side inside
> Foundry — there is no Python process for you to wrap. Anything you want
> to enforce above the model lives in the **Custom shared policies** layer
> from Task 10.02.

## Next

Continue to [10.02 — Author shared custom policies](10_02_custom_policies.md).

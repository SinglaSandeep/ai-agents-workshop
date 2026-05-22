---
title: Workshop Guide
layout: default
nav_order: 2
has_children: true
---

# AI Agents Workshop Guide

This guide walks through a local-first version of a FoundryIQ-style multi-agent assistant. You build the application agent by agent and verify a running version after every exercise.

## Exercises

1. [Setup](00_setup.md)
2. [Exercise 01: Build the HR agent](01_hr_agent.md)
3. [Exercise 02: Add the Products agent](02_products_agent.md)
4. [Exercise 03: Add the Marketing agent](03_marketing_agent.md)
5. [Exercise 04: Add the Orchestrator](04_orchestrator.md)
6. [Exercise 05: Add Observability for Microsoft Foundry](05_observability_ai_foundry.md)

## Scenario

Zava needs an internal assistant that can answer questions from different business domains. Instead of one large prompt, the app uses specialist agents:

- HR agent: PTO, benefits, handbook, and remote work policy
- Products agent: catalog, pricing, warranty, and specifications
- Marketing agent: campaigns, brand voice, audience, and channels
- Orchestrator: routes each user question to the best specialist

The workshop starts locally so learners can understand the agent pattern before replacing local markdown knowledge with FoundryIQ knowledge bases.

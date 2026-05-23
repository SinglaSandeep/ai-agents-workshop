---
title: '3. KQL queries'
layout: default
nav_order: 3
parent: 'Exercise 11: Observability'
---

# Task 11.03 — KQL Queries You'll Actually Use

## Introduction

A few small queries cover most day-to-day Pepsico-agents observability work:

## Tool calls in the last hour

```kql
dependencies
| where timestamp > ago(1h)
| where customDimensions has "gen_ai.operation.name"
| extend opName = tostring(customDimensions["gen_ai.operation.name"])
| extend toolName = tostring(customDimensions["gen_ai.tool.name"])
| extend toolArgs = tostring(customDimensions["gen_ai.tool.call.arguments"])
| project timestamp, name, opName, toolName, toolArgs
| order by timestamp desc
```

## Chat latency p50 / p95 by agent mode

```kql
requests
| where name == "POST /chat"
| extend mode = tostring(customDimensions["agent_mode"])
| summarize p50 = percentile(duration, 50),
            p95 = percentile(duration, 95),
            n = count()
  by mode
```

## Marketing-agent errors

```kql
dependencies
| where target contains "pepsico-marketing-agent"
| where success == false
| project timestamp, name, resultCode, customDimensions
| order by timestamp desc
```

## Continuous-eval pass rate (last 24h)

```kql
customMetrics
| where name == "azure_ai_evaluation/pass_rate"
| where timestamp > ago(24h)
| summarize avg(value) by bin(timestamp, 30m), tostring(customDimensions["agent_name"])
| render timechart
```

## Success

You now have a fully instrumented multi-agent assistant. Move on to
[Exercise 12 — Resource Cleanup](../12_cleanup/12_cleanup.md).

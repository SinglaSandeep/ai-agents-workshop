---
title: '1. Guardrails middleware'
layout: default
nav_order: 1
parent: 'Exercise 10: Guardrails & Red Teaming'
---

# Task 10.01 — Add the Content-Filter Middleware

## Introduction

Microsoft Foundry already applies model-side content safety. When a prompt
or response gets blocked, the underlying SDK raises
`OpenAIContentFilterException`. Without a guardrail, that surfaces to the
caller as a 500 error. A tiny **Agent Framework middleware** catches the
exception and returns a friendly refusal instead.

## Success Criteria

* The Marketing hosted agent returns a friendly refusal for clearly disallowed
  prompts and stays healthy.

## Key Tasks

### 01: Implement the middleware

Open [src/foundry_agents/marketing_hosted/middleware.py](https://github.com/SinglaSandeep/ai-agents-workshop/blob/main/src/foundry_agents/marketing_hosted/middleware.py).

<details markdown="block">
<summary><strong>Expand for the solution</strong></summary>

```python
"""Content-filter middleware for the hosted Marketing agent."""
from collections.abc import Awaitable, Callable

from agent_framework._middleware import ChatContext
from agent_framework._types import ChatResponse, Message
from agent_framework_openai._exceptions import OpenAIContentFilterException

CONTENT_FILTER_MESSAGE = (
    "I can’t help with that request because it violates Pepsico's content "
    "safety policies. If you have a safer or policy-compliant version of the "
    "question, I can help with that instead."
)


async def content_filter_middleware(
    context: ChatContext,
    call_next: Callable[[], Awaitable[None]],
) -> None:
    try:
        await call_next()
    except OpenAIContentFilterException:
        context.result = ChatResponse(
            messages=Message("assistant", [CONTENT_FILTER_MESSAGE]),
            finish_reason="stop",
        )
```

</details>

### 02: Wire it into the agent

In `main.py`, pass it to the `FoundryChatClient`:

```python
chat = FoundryChatClient(
    project_endpoint=PROJECT_ENDPOINT,
    model=MODEL_DEPLOYMENT,
    credential=credential,
    middleware=[content_filter_middleware],
)
```

### 03: Redeploy and test

```powershell
cd src/foundry_agents/marketing_hosted
azd ai agent up
azd ai agent invoke "<an obviously disallowed prompt>"
```

You should see the friendly refusal text rather than an HTTP error.

## Next

Continue to [10.02 — Author shared custom policies](10_02_custom_policies.md).

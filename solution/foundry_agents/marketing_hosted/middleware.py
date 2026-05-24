"""Content-filter middleware for the hosted Marketing agent.

Catches `OpenAIContentFilterException` and rewrites the result to a friendly
refusal so the caller sees a clean assistant message rather than a 500.
"""
from __future__ import annotations

from collections.abc import Awaitable, Callable

from agent_framework._middleware import ChatContext
from agent_framework._types import ChatResponse, Message
from agent_framework_openai._exceptions import OpenAIContentFilterException

CONTENT_FILTER_MESSAGE = (
    "I can’t help with that request because it violates Zava's content "
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

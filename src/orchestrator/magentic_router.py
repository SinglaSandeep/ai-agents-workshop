"""Magentic orchestrator that coordinates the Zava Foundry agents.

The orchestrator uses **Microsoft Agent Framework** (``agent-framework``)
and its ``MagenticBuilder`` planner. The Foundry hosted agents (Sales,
Inventory, Marketing, Action, Response Generator) are exposed to the
planner as *participants*; the planner picks which to call, in what order,
and synthesises the trail into prioritised actions.

Public surface
--------------
``build_workflow(credential)``
    Construct the Magentic workflow + participants. Used by the CLI
    runner and by ``--devui`` mode (DevUI registers the workflow as an
    entity).

``run_query(user_query, *, verbose=False)``
    Async helper that streams the workflow once and returns an
    :class:`OrchestratorResult`. When ``verbose=True`` it also pretty-prints
    every plan / progress-ledger / agent-output / final-answer event using
    Rich panels — mirroring the official ``workflow_magenticone`` sample
    at https://github.com/Azure-Samples/python-agentframework-demos.

Run:
    python -m src.orchestrator.runner --query "What is our PTO policy?"
    python -m src.orchestrator.runner --devui      # browser UI
"""

from __future__ import annotations

import json
import logging
from dataclasses import dataclass, field
from typing import Any, AsyncIterator

from src.common.settings import get_settings

LOG = logging.getLogger(__name__)


@dataclass
class OrchestratorResult:
    final_answer: str
    plan: list[str] = field(default_factory=list)
    transcripts: dict[str, str] = field(default_factory=dict)
    events: list[dict] = field(default_factory=list)


# --------------------------------------------------------------------------- #
# Workflow construction
# --------------------------------------------------------------------------- #


def build_workflow(credential: Any, *, manager_model: str | None = None) -> Any:
    """Build the Magentic workflow with all four Zava specialists.

    Accepts either an async (``azure.identity.aio.DefaultAzureCredential``)
    or sync (``azure.identity.DefaultAzureCredential``) credential — both
    ``FoundryChatClient`` and ``FoundryAgent`` accept either form.

    ``manager_model`` overrides the model deployment used by the Magentic
    *manager* (the orchestrator LLM). Hosted Foundry specialists are not
    affected — their model lives in the Foundry agent definition.
    """
    settings = get_settings()

    try:
        from agent_framework import Agent
        from agent_framework.foundry import FoundryAgent, FoundryChatClient
        from agent_framework.orchestrations import MagenticBuilder
    except ImportError as exc:  # pragma: no cover - import guard
        raise RuntimeError(
            'Install the framework extra: pip install -e ".[framework]"'
        ) from exc

    # FoundryChatClient drives the Magentic *manager* (no hosted agent_name).
    client = FoundryChatClient(
        project_endpoint=settings.azure_ai_project_endpoint,
        model=manager_model or settings.azure_ai_model_deployment,
        credential=credential,
    )

    # FoundryAgent(agent_name=...) references hosted specialists by name;
    # their model + instructions + tools live in the Foundry project.
    sales = FoundryAgent(
        project_endpoint=settings.azure_ai_project_endpoint,
        agent_name=settings.sales_agent_name,
        credential=credential,
        name="sales",
        description=(
            "Surfaces Zava SALES insights (revenue/units/margin trends by "
            "store, region, category, month and product) using the Sales MCP "
            "server backed by Cosmos DB."
        ),
    )
    inventory = FoundryAgent(
        project_endpoint=settings.azure_ai_project_endpoint,
        agent_name=settings.inventory_agent_name,
        credential=credential,
        name="inventory",
        description=(
            "Surfaces Zava distributor-level INVENTORY insights (low stock, "
            "overstock, weeks of cover, reorder needs across 4 distributors / "
            "6 warehouses) using the Inventory MCP server backed by Cosmos DB."
        ),
    )
    marketing = FoundryAgent(
        project_endpoint=settings.azure_ai_project_endpoint,
        agent_name=settings.marketing_agent_name,
        credential=credential,
        name="marketing",
        description=(
            "Answers questions about Zava marketing campaigns (status, KPIs, "
            "budgets, ROI, target stores/categories) using the Marketing MCP "
            "server (Cosmos DB) joined with the Foundry IQ knowledge base of "
            "briefs/post-mortems, plus Bing web_search for live context."
        ),
    )
    action = FoundryAgent(
        project_endpoint=settings.azure_ai_project_endpoint,
        agent_name=settings.action_agent_name,
        credential=credential,
        name="action",
        description=(
            "Turns the sales / inventory / marketing INSIGHTS into a short, "
            "prioritised set of concrete cross-domain operational ACTIONS and "
            "writes the final user-facing reply (with an optional chart). "
            "Always call this last."
        ),
    )

    manager = Agent(
        client=client,
        name="manager",
        description="Magentic manager that coordinates Zava insights-to-action agents.",
        instructions=(
            "Coordinate Zava specialists to turn data into action for a "
            "store/ops manager. Call the relevant insight specialists "
            "(`sales`, `inventory`, `marketing`) — often more than one, since "
            "the best actions connect domains; reuse shared keys (store_id, "
            "region, category, product_id, campaign_id). Finish by calling "
            "`action`, which produces the prioritised recommendations and a "
            "draft reply (with an optional ```chart block). A separate "
            "Response Generator then writes the polished final reply, so make "
            "sure `action` runs last. Be efficient: call each needed agent "
            "ONCE, skip irrelevant ones, and avoid redundant rounds."
        ),
    )

    workflow = MagenticBuilder(
        participants=[sales, inventory, marketing, action],
        manager_agent=manager,
        max_round_count=7,
        max_stall_count=2,
        max_reset_count=1,
    ).build()
    return workflow


# --------------------------------------------------------------------------- #
# Pretty-printing of streamed events (mirrors workflow_magenticone.py)
# --------------------------------------------------------------------------- #


def _handle_event(event: Any, console: Any, state: dict) -> None:
    """Render a single ``WorkflowEvent`` to the console and collect state."""
    from rich.markdown import Markdown
    from rich.panel import Panel

    try:
        from agent_framework import AgentResponseUpdate
    except ImportError:  # pragma: no cover
        AgentResponseUpdate = None  # type: ignore[assignment]

    try:
        from agent_framework.orchestrations import MagenticProgressLedger
    except ImportError:  # pragma: no cover
        MagenticProgressLedger = None  # type: ignore[assignment]

    etype = getattr(event, "type", "")
    executor = getattr(event, "executor_id", "?")

    # ---- Orchestrator events: plan, task ledger, progress ledger --------
    if etype == "magentic_orchestrator":
        data = getattr(event, "data", None)
        if data is None:
            return
        event_type_name = getattr(getattr(data, "event_type", ""), "name", "?")
        state["events"].append({"type": "manager", "kind": event_type_name})
        emoji = "✅" if event_type_name == "PROGRESS_LEDGER_UPDATED" else "🧭"
        content = getattr(data, "content", None)

        if MagenticProgressLedger and isinstance(content, MagenticProgressLedger):
            rendered: Any = json.dumps(content.to_dict(), indent=2)
            border = "bold yellow"
        elif hasattr(content, "text"):
            rendered = Markdown(content.text)
            border = "bold green"
        else:
            rendered = Markdown(str(content))
            border = "bold green"
        console.print()
        console.print(
            Panel(
                rendered,
                title=f"{emoji} Orchestrator: {event_type_name}",
                border_style=border,
                padding=(1, 2),
            )
        )
        return

    # ---- Streaming tokens from a participant ----------------------------
    if etype == "output" and AgentResponseUpdate and isinstance(event.data, AgentResponseUpdate):
        update = event.data
        msg_id = getattr(update, "message_id", None)
        if msg_id != state.get("last_msg_id"):
            if state.get("last_msg_id") is not None:
                console.print()
            console.print(f"🤖 [bold cyan]{executor}[/bold cyan]:", end=" ")
            state["last_msg_id"] = msg_id
        text = getattr(update, "text", "") or ""
        console.print(text, end="")
        state["transcripts"].setdefault(executor, "")
        state["transcripts"][executor] += text
        return

    # ---- Participant finished — render its full output ------------------
    if etype == "executor_completed":
        data = event.data
        parts: list[str] = []
        if AgentResponseUpdate and isinstance(data, list):
            parts = [
                getattr(msg, "text", "") or ""
                for msg in data
                if isinstance(msg, AgentResponseUpdate)
            ]
        full_text = "".join(parts).strip()
        if full_text:
            state["transcripts"][executor] = full_text
            state["plan"].append(executor)
            console.print()
            console.print(
                Panel(
                    Markdown(full_text),
                    title=f"🤖 {executor}",
                    border_style="cyan",
                    padding=(1, 2),
                )
            )
        return

    # ---- Whole-agent response event (non-streaming) ---------------------
    if etype == "agent_response":
        data = event.data
        name = getattr(data, "agent_name", executor)
        text = getattr(data, "text", "") or ""
        if text:
            state["transcripts"][name] = text
            state["plan"].append(name)
            if name == "action":
                state["final_answer"] = text
            console.print()
            console.print(
                Panel(
                    Markdown(text),
                    title=f"🤖 {name}",
                    border_style="cyan",
                    padding=(1, 2),
                )
            )
        return

    # ---- Final workflow output ------------------------------------------
    if etype == "output":
        data = event.data
        text = getattr(data, "text", None)
        if text is None and isinstance(data, list) and data:
            text = getattr(data[-1], "text", str(data[-1]))
        if text and not state.get("final_answer"):
            state["final_answer"] = text


def _collect_event_quiet(event: Any, state: dict) -> None:
    """Collect transcripts / plan / final answer without printing anything."""
    etype = getattr(event, "type", "")
    if etype == "magentic_orchestrator":
        data = getattr(event, "data", None)
        if data is not None:
            kind = getattr(getattr(data, "event_type", ""), "name", "?")
            state["events"].append({"type": "manager", "kind": kind})
            LOG.info("manager %s", kind)
    elif etype == "agent_response":
        data = event.data
        name = getattr(data, "agent_name", getattr(event, "executor_id", "?"))
        text = getattr(data, "text", "") or ""
        if text:
            state["transcripts"][name] = text
            state["plan"].append(name)
            if name == "action":
                state["final_answer"] = text
    elif etype == "output":
        data = event.data
        text = getattr(data, "text", None)
        if text is None and isinstance(data, list) and data:
            text = getattr(data[-1], "text", str(data[-1]))
        if text and not state["final_answer"]:
            state["final_answer"] = text


# --------------------------------------------------------------------------- #
# Session memory (in-process, per conversation_id)
# --------------------------------------------------------------------------- #
# Magentic only accepts a single task message per run, so session memory works
# by folding recent turns into that task string. Stored in RAM only — scoped to
# the conversation_id supplied by the caller and cleared on restart.
_MAX_HISTORY_TURNS = 6
_SESSIONS: dict[str, list[tuple[str, str]]] = {}


def _compose_task(user_query: str, conversation_id: str | None) -> str:
    """Wrap the new question with recent turns as clearly-labelled context.

    The manager must understand that the prior turns are *read-only
    background* (only there so follow-ups like "and the second one?" or
    "do the same for inventory" make sense) and that the single thing it
    has to plan for and answer is the CURRENT REQUEST. Without this strict
    framing the manager tends to re-answer earlier questions or merge them
    into the new one.
    """
    if not conversation_id:
        return user_query
    history = _SESSIONS.get(conversation_id)
    if not history:
        return user_query

    lines = [
        "You are continuing an ongoing conversation with the same user.",
        "",
        "=== PRIOR CONVERSATION (read-only context, already answered) ===",
    ]
    for q, a in history:
        lines.append(f"User asked: {q}")
        lines.append(f"You answered: {a}")
        lines.append("")
    lines.append("=== END PRIOR CONVERSATION ===")
    lines.append("")
    lines.append(
        "Use the prior conversation ONLY to resolve references in the new "
        "request (e.g. pronouns, 'that product', 'the same for ...', "
        "'those stores'). Do NOT re-answer earlier questions. Plan for and "
        "answer ONLY the current request below."
    )
    lines.append("")
    lines.append(f"CURRENT REQUEST: {user_query}")
    return "\n".join(lines)


def _remember(conversation_id: str | None, user_query: str, answer: str) -> None:
    """Store the latest turn, keeping only the most recent turns."""
    if not conversation_id or not answer:
        return
    history = _SESSIONS.setdefault(conversation_id, [])
    history.append((user_query, answer))
    if len(history) > _MAX_HISTORY_TURNS:
        del history[: len(history) - _MAX_HISTORY_TURNS]


def _compose_intent_input(user_query: str, conversation_id: str | None) -> str:
    """Wrap the new message with recent turns for the Intent Detector.

    Uses the SAME shared session memory (``_SESSIONS``) as the Magentic flow,
    so a short follow-up that only makes sense in context (e.g. "and the
    second one?", "do the same for inventory") is still seen as a continuation
    of the business thread rather than an out-of-context one-liner.
    """
    if not conversation_id:
        return user_query
    history = _SESSIONS.get(conversation_id)
    if not history:
        return user_query

    lines = ["=== RECENT CONVERSATION (context only) ==="]
    for q, _a in history:
        lines.append(f"User: {q}")
    lines.append("=== END CONTEXT ===")
    lines.append("")
    lines.append(f"Classify ONLY this latest user message: {user_query}")
    return "\n".join(lines)


# --------------------------------------------------------------------------- #
# Intent detection + Response Generator (conditional routing)
# --------------------------------------------------------------------------- #
# A lightweight Intent Detector classifies each turn as GENERAL (greeting /
# small talk) or BUSINESS. GENERAL turns short-circuit to the Response
# Generator for a quick friendly reply; BUSINESS turns run the full Magentic
# flow and the Response Generator then writes the final reply from the
# specialists' + action recommender's transcripts.
import re

_CHART_RE = re.compile(r"```chart\s*[\s\S]*?```", re.IGNORECASE)
_GREETING_HINTS = (
    "hi", "hello", "hey", "yo", "hiya", "thanks", "thank you", "thank",
    "good morning", "good afternoon", "good evening", "how are you",
    "who are you", "what can you do", "what do you do", "help", "bye",
    "goodbye", "see you", "cheers",
)


async def _run_foundry_agent(agent_name: str, prompt: str, credential: Any) -> str:
    """Invoke a single hosted Foundry agent and return its text answer."""
    from agent_framework.foundry import FoundryAgent

    settings = get_settings()
    async with FoundryAgent(
        project_endpoint=settings.azure_ai_project_endpoint,
        agent_name=agent_name,
        credential=credential,
    ) as agent:
        response = await agent.run(prompt)
        return getattr(response, "text", str(response)) or ""


async def _detect_intent(user_query: str, credential: Any, conversation_id: str | None = None) -> str:
    """Classify the raw user message as ``"general"`` or ``"business"``.

    Shares the same per-conversation session memory as the Magentic flow
    (``_SESSIONS``) so short follow-ups (e.g. "and the second one?") that only
    make sense in context are still classified correctly.
    """
    settings = get_settings()
    prompt = _compose_intent_input(user_query, conversation_id)
    try:
        raw = await _run_foundry_agent(settings.intent_agent_name, prompt, credential)
        token = raw.strip().upper()
        if "GENERAL" in token and "BUSINESS" not in token:
            return "general"
        if "BUSINESS" in token:
            return "business"
    except Exception:  # pragma: no cover - fall back to heuristic
        LOG.warning("[orchestrator] intent detector failed; using heuristic", exc_info=True)

    q = user_query.strip().lower().rstrip("!.?")
    if len(q.split()) <= 4 and any(q == h or q.startswith(h + " ") or q == h for h in _GREETING_HINTS):
        return "general"
    if q in _GREETING_HINTS:
        return "general"
    return "business"


def _extract_chart_blocks(text: str) -> list[str]:
    return _CHART_RE.findall(text or "")


async def _respond_general(user_query: str, credential: Any) -> str:
    """Quick friendly reply for greetings / small talk via the Response Generator."""
    settings = get_settings()
    prompt = (
        "GENERAL turn. The user sent a conversational message (greeting, "
        "thanks, small talk, or a question about what you can do). Reply "
        "briefly and warmly in the Zava voice. Do NOT add a chart and do NOT "
        "add a 'Sources:' line.\n\n"
        f"User: {user_query}"
    )
    return await _run_foundry_agent(settings.response_agent_name, prompt, credential)


async def _finalize_with_response_generator(
    user_query: str,
    transcripts: dict[str, str],
    draft: str,
    credential: Any,
) -> str:
    """Compose the final user-facing reply from the specialist transcripts.

    Any ```chart block produced by the action recommender is preserved: the
    Response Generator is instructed to keep it verbatim, and as a deterministic
    safety net it is re-appended if the generator dropped it.
    """
    settings = get_settings()
    parts = [
        "BUSINESS turn. Write the final user-facing reply from these findings.",
        "",
        f"User question: {user_query}",
        "",
        "Specialist findings:",
    ]
    for name, text in transcripts.items():
        if text and text.strip():
            parts.append(f"[{name}]")
            parts.append(text.strip())
            parts.append("")
    parts.append(
        "Synthesise the findings and surface the recommended ACTIONS. If the "
        "action recommender included a ```chart block, KEEP that exact chart "
        "block verbatim in your reply."
    )
    prompt = "\n".join(parts)
    reply = await _run_foundry_agent(settings.response_agent_name, prompt, credential)

    # Deterministic chart safety net: make sure any chart the action agent
    # generated survives even if the Response Generator omitted it.
    charts = _extract_chart_blocks(draft)
    if charts and "```chart" not in (reply or "").lower():
        reply = (reply or "").rstrip() + "\n\n## Snapshot\n\n" + charts[0]
    return reply or draft


# --------------------------------------------------------------------------- #
# Public async entry point
# --------------------------------------------------------------------------- #


async def run_query(
    user_query: str,
    *,
    verbose: bool = False,
    manager_model: str | None = None,
    conversation_id: str | None = None,
) -> OrchestratorResult:
    """Plan + execute a query across the Zava specialist agents.

    Parameters
    ----------
    user_query:
        Natural language question.
    verbose:
        When ``True``, pretty-prints every orchestrator and agent event
        (plan, progress ledger, per-agent transcripts, final answer) to
        stdout using Rich panels. Default ``False`` — quiet, suitable for
        the chat backend.
    manager_model:
        Optional deployment name for the Magentic *manager* model. Lets
        callers swap the orchestrator LLM per request without redeploying.
    """
    from azure.identity.aio import DefaultAzureCredential

    state: dict[str, Any] = {
        "plan": [],
        "transcripts": {},
        "events": [],
        "final_answer": "",
        "last_msg_id": None,
    }

    console = None
    if verbose:
        import sys

        # Make sure emoji / box-drawing chars survive Windows code page 1252.
        for stream in (sys.stdout, sys.stderr):
            reconfigure = getattr(stream, "reconfigure", None)
            if reconfigure is not None:
                try:
                    reconfigure(encoding="utf-8")
                except Exception:  # pragma: no cover - best effort
                    pass

        from rich.console import Console
        from rich.panel import Panel

        console = Console()
        console.print()
        console.print(Panel(user_query, title="User Query", border_style="bold blue"))

    task = _compose_task(user_query, conversation_id)

    async with DefaultAzureCredential() as cred:
        # Intent Detector — conditional edge. GENERAL turns skip Magentic and
        # go straight to the Response Generator. Shares session memory.
        intent = await _detect_intent(user_query, cred, conversation_id)
        state["events"].append({"type": "intent", "intent": intent})
        LOG.info("[orchestrator] intent=%s", intent)
        if verbose and console is not None:
            console.print()
            console.print(Panel(intent, title="🧭 Intent", border_style="bold magenta"))

        if intent == "general":
            reply = await _respond_general(user_query, cred)
            state["final_answer"] = reply
            state["plan"] = ["intent", "response"]
        else:
            workflow = build_workflow(cred, manager_model=manager_model)

            async for event in workflow.run(task, stream=True):
                if verbose:
                    _handle_event(event, console, state)
                else:
                    _collect_event_quiet(event, state)

            # The action recommender's text is the draft (carries any chart);
            # the Response Generator writes the final user-facing reply.
            draft = state["final_answer"]
            if not draft and state["transcripts"]:
                draft = next(reversed(state["transcripts"].values()))
            reply = await _finalize_with_response_generator(
                user_query, state["transcripts"], draft, cred
            )
            state["final_answer"] = reply
            if "response" not in state["plan"]:
                state["plan"].append("response")

    result = OrchestratorResult(
        final_answer=state["final_answer"],
        plan=state["plan"],
        transcripts=state["transcripts"],
        events=state["events"],
    )

    if not result.final_answer and result.transcripts:
        # Fallback if no agent produced a final answer
        result.final_answer = next(reversed(result.transcripts.values()))

    _remember(conversation_id, user_query, result.final_answer)

    if verbose and console is not None:
        from rich.markdown import Markdown
        from rich.panel import Panel

        console.print()
        console.print(
            Panel(
                Markdown(result.final_answer or "_(no answer produced)_"),
                title="🌍 Final Answer",
                border_style="bold green",
                padding=(1, 2),
            )
        )

    return result


# --------------------------------------------------------------------------- #
# Streaming entry point (for the live web UI)
# --------------------------------------------------------------------------- #


def _event_to_payload(event: Any, state: dict) -> list[dict]:
    """Translate a single workflow event into one or more JSON payloads.

    Each payload is a plain ``dict`` (JSON-serialisable) with a ``type``
    discriminator the frontend can switch on:

    * ``manager``    — planner / progress-ledger updates from the Magentic
                       manager (``event_kind`` carries TASK_LEDGER,
                       PROGRESS_LEDGER_UPDATED, FINAL_ANSWER, …).
    * ``token``      — streaming token chunk from a specialist.
    * ``agent``      — a specialist finished and produced a full transcript.
    * ``final``      — workflow output (final answer).
    """
    try:
        from agent_framework import AgentResponseUpdate  # type: ignore
    except ImportError:  # pragma: no cover
        AgentResponseUpdate = None  # type: ignore[assignment]

    payloads: list[dict] = []
    etype = getattr(event, "type", "")
    executor = getattr(event, "executor_id", "?")

    if etype == "magentic_orchestrator":
        data = getattr(event, "data", None)
        if data is None:
            return payloads
        kind = getattr(getattr(data, "event_type", ""), "name", "?")
        content = getattr(data, "content", None)
        if hasattr(content, "to_dict"):
            text = json.dumps(content.to_dict(), indent=2)
        elif hasattr(content, "text"):
            text = content.text or ""
        else:
            text = str(content) if content is not None else ""
        state["events"].append({"type": "manager", "kind": kind})
        payloads.append({"type": "manager", "kind": kind, "text": text})
        return payloads

    if (
        etype == "output"
        and AgentResponseUpdate is not None
        and isinstance(getattr(event, "data", None), AgentResponseUpdate)
    ):
        update = event.data
        text = getattr(update, "text", "") or ""
        if text:
            state["transcripts"].setdefault(executor, "")
            state["transcripts"][executor] += text
            payloads.append({"type": "token", "agent": executor, "text": text})
        return payloads

    if etype == "agent_response":
        data = event.data
        name = getattr(data, "agent_name", executor)
        text = getattr(data, "text", "") or ""
        if text:
            state["transcripts"][name] = text
            if name not in state["plan"]:
                state["plan"].append(name)
            if name == "action":
                state["final_answer"] = text
            payloads.append({"type": "agent", "agent": name, "text": text})
        return payloads

    if etype == "executor_completed":
        data = event.data
        parts: list[str] = []
        if AgentResponseUpdate is not None and isinstance(data, list):
            parts = [
                getattr(msg, "text", "") or ""
                for msg in data
                if isinstance(msg, AgentResponseUpdate)
            ]
        full_text = "".join(parts).strip()
        if full_text:
            state["transcripts"][executor] = full_text
            if executor not in state["plan"]:
                state["plan"].append(executor)
            payloads.append({"type": "agent", "agent": executor, "text": full_text})
        return payloads

    if etype == "output":
        data = event.data
        text = getattr(data, "text", None)
        if text is None and isinstance(data, list) and data:
            text = getattr(data[-1], "text", str(data[-1]))
        if text and not state["final_answer"]:
            state["final_answer"] = text
            payloads.append({"type": "final", "text": text})
        return payloads

    return payloads


def _log_payload(payload: dict) -> None:
    """Emit a one-line summary of an orchestrator payload to the app logger.

    Shows up in the uvicorn console so you can follow the multi-agent flow
    without watching the browser. Long text is truncated.
    """
    kind = payload.get("type")
    if kind == "manager":
        text = (payload.get("text") or "").replace("\n", " ")
        if len(text) > 200:
            text = text[:200] + "…"
        LOG.info("[orchestrator] manager %s | %s", payload.get("kind", "?"), text)
    elif kind == "token":
        # Token-level chunks are very chatty; log only when DEBUG is on.
        LOG.debug("[orchestrator] token  %-18s | %s", payload.get("agent", "?"), payload.get("text", ""))
    elif kind == "agent":
        text = (payload.get("text") or "").replace("\n", " ")
        LOG.info(
            "[orchestrator] agent  %-18s | %d chars: %s",
            payload.get("agent", "?"),
            len(payload.get("text") or ""),
            text[:160] + ("…" if len(text) > 160 else ""),
        )
    elif kind == "final":
        LOG.info("[orchestrator] final  | %d chars", len(payload.get("text") or ""))
    elif kind == "error":
        LOG.error("[orchestrator] error  | %s", payload.get("message"))


async def stream_query(
    user_query: str,
    *,
    manager_model: str | None = None,
    conversation_id: str | None = None,
) -> AsyncIterator[dict]:
    """Yield structured events from the orchestrator as they happen.

    Designed for an SSE / chunked HTTP response so the browser can render
    plan steps, per-agent transcripts and the final answer in real time.
    The first event is always ``{"type": "start", ...}``; the last is
    ``{"type": "done", "plan": [...], "final": "..."}``.

    ``manager_model`` lets the caller pick the orchestrator model per
    request — no redeploy needed.
    """
    from azure.identity.aio import DefaultAzureCredential

    state: dict[str, Any] = {
        "plan": [],
        "transcripts": {},
        "events": [],
        "final_answer": "",
    }

    LOG.info(
        "[orchestrator] START query=%r manager_model=%s",
        user_query,
        manager_model or "(default)",
    )
    yield {"type": "start", "query": user_query, "manager_model": manager_model}

    reply = ""
    try:
        async with DefaultAzureCredential() as cred:
            # Intent Detector — conditional edge (shares session memory).
            intent = await _detect_intent(user_query, cred, conversation_id)
            state["events"].append({"type": "intent", "intent": intent})
            LOG.info("[orchestrator] intent=%s", intent)
            yield {"type": "intent", "intent": intent}

            if intent == "general":
                # GENERAL turn → straight to the Response Generator.
                reply = await _respond_general(user_query, cred)
                state["final_answer"] = reply
                state["plan"] = ["intent", "response"]
                _log_payload({"type": "agent", "agent": "response", "text": reply})
                yield {"type": "response", "agent": "response", "intent": "general", "text": reply}
            else:
                # BUSINESS turn → full Magentic flow, then the Response
                # Generator writes the final reply.
                task = _compose_task(user_query, conversation_id)
                workflow = build_workflow(cred, manager_model=manager_model)
                async for event in workflow.run(task, stream=True):
                    for payload in _event_to_payload(event, state):
                        # The Response Generator produces the real final reply,
                        # so suppress Magentic's own "final" payload.
                        if payload.get("type") == "final":
                            continue
                        _log_payload(payload)
                        yield payload

                draft = state["final_answer"]
                if not draft and state["transcripts"]:
                    draft = next(reversed(state["transcripts"].values()))
                reply = await _finalize_with_response_generator(
                    user_query, state["transcripts"], draft, cred
                )
                state["final_answer"] = reply
                if "response" not in state["plan"]:
                    state["plan"].append("response")
                _log_payload({"type": "agent", "agent": "response", "text": reply})
                yield {"type": "response", "agent": "response", "intent": "business", "text": reply}
    except Exception as exc:  # pragma: no cover - surface to UI
        LOG.exception("Orchestrator stream failed")
        yield {"type": "error", "message": str(exc)}
        return

    _remember(conversation_id, user_query, reply)

    LOG.info(
        "[orchestrator] DONE plan=%s final_chars=%d",
        " -> ".join(state["plan"]) or "(none)",
        len(reply or ""),
    )
    yield {
        "type": "done",
        "final": reply,
        "plan": state["plan"],
        "transcripts": state["transcripts"],
    }

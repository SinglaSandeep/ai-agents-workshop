"""CLI entry point to exercise the Magentic orchestrator from the terminal.

Modes
-----
``--query "..."``
    Run a single query and stream every orchestrator + specialist event to
    the console (Rich panels: plan, progress ledger, per-agent transcripts,
    final answer). Pass ``--json`` to additionally emit the structured
    result as JSON at the end.

``--devui``
    Launch the Agent Framework DevUI in the browser with the whole
    Magentic workflow registered as a single entity. The DevUI lets you
    chat with the orchestrator and inspect the plan + intermediate agent
    calls visually. Same pattern as the ``workflow_magenticone.py`` sample
    in https://github.com/Azure-Samples/python-agentframework-demos.

Examples
--------
.. code-block:: powershell

    python -m src.orchestrator.runner --query "What is our PTO policy?"
    python -m src.orchestrator.runner --devui
    python -m src.orchestrator.runner --devui --port 8090
"""

from __future__ import annotations

import argparse
import asyncio
import json
import logging
import os

from .magentic_router import (
    _detect_intent,
    _respond_general,
    build_workflow,
    run_query,
)


def _run_devui(host: str, port: int) -> None:
    """Launch DevUI with the Magentic workflow as the registered entity."""
    import json as _json
    import uuid
    from datetime import datetime, timezone

    from agent_framework import (
        AgentResponse,
        AgentResponseUpdate,
        Content,
        ResponseStream,
        WorkflowAgent,
    )
    from agent_framework.devui import register_cleanup, serve
    from azure.identity import DefaultAzureCredential

    credential = DefaultAzureCredential(exclude_interactive_browser_credential=False)
    workflow = build_workflow(credential)

    def _now() -> str:
        return datetime.now(tz=timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%fZ")

    def _latest_user_text(messages) -> str:
        """Best-effort extraction of the newest user text from DevUI input."""
        if messages is None:
            return ""
        if isinstance(messages, str):
            return messages
        items = messages if isinstance(messages, (list, tuple)) else [messages]
        texts: list[str] = []
        for m in items:
            if isinstance(m, str):
                texts.append(m)
                continue
            t = getattr(m, "text", None)
            if t:
                texts.append(t)
                continue
            for c in getattr(m, "contents", None) or []:
                ct = getattr(c, "text", None)
                if ct:
                    texts.append(ct)
        return texts[-1] if texts else ""

    class VerboseWorkflowAgent(WorkflowAgent):
        """WorkflowAgent that also forwards Magentic orchestrator events.

        The stock ``WorkflowAgent`` drops ``magentic_orchestrator`` events
        (plan / task-ledger / progress-ledger), so the DevUI chat shows only
        the final answer. This subclass converts those events into
        ``AgentResponseUpdate`` text chunks tagged with an author name so
        users see the planner's reasoning live in the conversation.

        It also applies the SAME intent gate as the FastAPI app: a GENERAL
        turn (greeting / thanks / small talk) is answered directly by the
        Response Generator and the Magentic manager is NOT invoked. Only
        BUSINESS turns run the full workflow.
        """

        def run(  # type: ignore[override]
            self,
            messages=None,
            *,
            stream: bool = False,
            **kwargs,
        ):
            response_id = str(uuid.uuid4())
            if stream:
                return ResponseStream(
                    self._gated_stream(messages, response_id, kwargs),
                    finalizer=AgentResponse.from_updates,
                )
            return self._gated_response(messages, response_id, kwargs)

        async def _gated_response(self, messages, response_id, run_kwargs):
            updates = [u async for u in self._gated_stream(messages, response_id, run_kwargs)]
            return AgentResponse.from_updates(updates)

        async def _gated_stream(self, messages, response_id, run_kwargs):
            from azure.identity.aio import DefaultAzureCredential as AsyncCredential

            log = logging.getLogger("zava.orchestrator")
            user_text = _latest_user_text(messages)
            if user_text:
                try:
                    async with AsyncCredential() as cred:
                        intent = await _detect_intent(user_text, cred, None, None)
                        log.info("[devui] intent=%s", intent)
                        if intent == "general":
                            reply = await _respond_general(user_text, cred, None)
                            yield AgentResponseUpdate(
                                contents=[Content.from_text(text=reply)],
                                role="assistant",
                                author_name="response",
                                response_id=response_id,
                                message_id=str(uuid.uuid4()),
                                created_at=_now(),
                            )
                            return
                except Exception:  # pragma: no cover - fall back to full workflow
                    log.warning(
                        "[devui] intent gate failed; running full workflow",
                        exc_info=True,
                    )
            # BUSINESS turn (or gate failed) → full Magentic workflow.
            inner = WorkflowAgent.run(self, messages, stream=True, **run_kwargs)
            async for update in inner:
                yield update

        def _convert_workflow_event_to_agent_response_updates(  # type: ignore[override]
            self, response_id: str, event
        ):
            updates = super()._convert_workflow_event_to_agent_response_updates(
                response_id, event
            )
            etype = getattr(event, "type", "")
            if etype != "magentic_orchestrator":
                return updates

            data = getattr(event, "data", None)
            if data is None:
                return updates
            event_type_name = getattr(getattr(data, "event_type", ""), "name", "?")
            content = getattr(data, "content", None)

            if hasattr(content, "to_dict"):
                rendered = (
                    f"**[{event_type_name}]**\n\n```json\n"
                    f"{_json.dumps(content.to_dict(), indent=2)}\n```"
                )
            elif hasattr(content, "text"):
                rendered = f"**[{event_type_name}]**\n\n{content.text}"
            else:
                rendered = f"**[{event_type_name}]**\n\n{content}"

            updates.append(
                AgentResponseUpdate(
                    contents=[Content.from_text(text=rendered + "\n\n")],
                    role="assistant",
                    author_name="orchestrator",
                    response_id=response_id,
                    message_id=str(uuid.uuid4()),
                    created_at=datetime.now(tz=timezone.utc).strftime(
                        "%Y-%m-%dT%H:%M:%S.%fZ"
                    ),
                )
            )
            return updates

    # Wrap the workflow as a chat-style agent so DevUI shows a plain text
    # input box (not the structured ChatMessage schema editor) AND streams
    # planner / progress-ledger / specialist updates inline.
    agent = VerboseWorkflowAgent(
        workflow=workflow,
        name="zava_orchestrator",
        description=(
            "Zava Magentic orchestrator. Plans across the Store-Ops, "
            "Products, Marketing and Response-Generator Foundry agents "
            "and synthesises a single final answer."
        ),
    )

    # Close the shared credential on DevUI shutdown.
    register_cleanup(agent, credential.close)

    logging.getLogger("zava.orchestrator").info(
        "Launching DevUI on http://%s:%d (entity: zava_orchestrator)", host, port
    )
    serve(
        entities=[agent],
        host=host,
        port=port,
        auto_open=True,
        auth_enabled=False,
    )


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    parser = argparse.ArgumentParser(
        description="Run a query through the Zava Magentic orchestrator, or launch DevUI."
    )
    parser.add_argument("--query", help="The user question (CLI mode).")
    parser.add_argument(
        "--devui",
        action="store_true",
        help="Launch the Agent Framework DevUI in the browser instead of running a single query.",
    )
    parser.add_argument(
        "--host",
        default=os.getenv("DEVUI_HOST", "127.0.0.1"),
        help="DevUI bind host (default: %(default)s).",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=int(os.getenv("DEVUI_PORT", "8081")),
        help="DevUI bind port (default: %(default)s).",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="(CLI mode) emit the structured result as JSON after the rich trace.",
    )
    parser.add_argument(
        "--quiet",
        action="store_true",
        help="(CLI mode) suppress rich event panels; only print the final answer.",
    )
    args = parser.parse_args()

    if args.devui:
        _run_devui(args.host, args.port)
        return

    if not args.query:
        parser.error("either --query or --devui is required")

    result = asyncio.run(run_query(args.query, verbose=not args.quiet))

    if args.quiet:
        print("\n=== Plan ===")
        print(" -> ".join(result.plan) or "(no plan)")
        print("\n=== Final Answer ===")
        print(result.final_answer)

    if args.json:
        print(
            "\n=== JSON ===\n"
            + json.dumps(
                {
                    "final_answer": result.final_answer,
                    "plan": result.plan,
                    "transcripts": result.transcripts,
                    "events": result.events,
                },
                indent=2,
            )
        )


if __name__ == "__main__":
    main()

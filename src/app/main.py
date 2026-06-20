"""FastAPI chat application for the Zava multi-agent assistant."""

from __future__ import annotations

import json
import logging
import os
import secrets
from pathlib import Path

from dotenv import load_dotenv
from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.responses import HTMLResponse, JSONResponse, StreamingResponse
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from pydantic import BaseModel, Field

from src.common.observability import configure_observability, trace_span
from src.orchestrator.magentic_router import run_query, stream_query

load_dotenv()

# Surface orchestrator events (manager plans, per-agent transcripts, final
# answer) in the uvicorn console so you can follow the flow without watching
# the browser.
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)-7s %(name)s | %(message)s",
    datefmt="%H:%M:%S",
)
logging.getLogger("src.orchestrator").setLevel(logging.INFO)

app = FastAPI(title="Zava AI Agents Workshop", version="1.0.0")
observability_enabled = configure_observability(app)
_CHAT_HTML_PATH = Path(__file__).with_name("chat.html")


# --------------------------- HTTP Basic Auth --------------------------------
# Credentials come from environment variables so they never live in source.
# In Container Apps we set BASIC_AUTH_USERNAME / BASIC_AUTH_PASSWORD as
# secrets. If either is unset (e.g. running purely locally for dev), auth
# is disabled and the app behaves as before.
_BASIC_AUTH_USERNAME = os.environ.get("BASIC_AUTH_USERNAME", "").strip()
_BASIC_AUTH_PASSWORD = os.environ.get("BASIC_AUTH_PASSWORD", "")
_BASIC_AUTH_ENABLED = bool(_BASIC_AUTH_USERNAME and _BASIC_AUTH_PASSWORD)
_basic_auth_scheme = HTTPBasic(auto_error=False)


def require_basic_auth(
    credentials: HTTPBasicCredentials | None = Depends(_basic_auth_scheme),
) -> str:
    """Validate HTTP Basic credentials using constant-time comparison."""
    if not _BASIC_AUTH_ENABLED:
        return "anonymous"
    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required",
            headers={"WWW-Authenticate": 'Basic realm="Zava"'},
        )
    user_ok = secrets.compare_digest(
        credentials.username.encode("utf-8"),
        _BASIC_AUTH_USERNAME.encode("utf-8"),
    )
    pass_ok = secrets.compare_digest(
        credentials.password.encode("utf-8"),
        _BASIC_AUTH_PASSWORD.encode("utf-8"),
    )
    if not (user_ok and pass_ok):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
            headers={"WWW-Authenticate": 'Basic realm="Zava"'},
        )
    return credentials.username


class ChatRequest(BaseModel):
    query: str = Field(..., min_length=1, examples=["What is our PTO policy?"])
    model: str | None = Field(
        default=None,
        description="Optional Foundry model deployment name for the orchestrator manager.",
    )
    conversation_id: str | None = Field(
        default=None,
        description="Optional client-supplied id used to carry session history across turns.",
    )


# Comma-separated list of allowed deployment names the UI may pick. Defaults to
# the chat models the infra repo deploys; override at deploy time with
# ORCHESTRATOR_MODEL_CHOICES="gpt-4.1-mini,gpt-5.4-mini,gpt-5.4-nano".
_DEFAULT_MODEL_CHOICES = "gpt-4.1-mini,gpt-5.4-mini,gpt-5.4-nano"
_ALLOWED_MODELS = [
    m.strip()
    for m in os.environ.get("ORCHESTRATOR_MODEL_CHOICES", _DEFAULT_MODEL_CHOICES).split(",")
    if m.strip()
]
_DEFAULT_MODEL = os.environ.get("AZURE_AI_MODEL_DEPLOYMENT", _ALLOWED_MODELS[0] if _ALLOWED_MODELS else "gpt-4.1-mini")


def _resolve_model(requested: str | None) -> str | None:
    """Return a safe model name to forward to the orchestrator (or None)."""
    if not requested:
        return None
    if requested not in _ALLOWED_MODELS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Model {requested!r} is not in allowed list: {_ALLOWED_MODELS}",
        )
    return requested


@app.get("/health")
def health() -> dict[str, object]:
    return {
        "status": "ok",
        "observability_enabled": observability_enabled,
        "auth_enabled": _BASIC_AUTH_ENABLED,
    }


@app.get("/models")
def models(_user: str = Depends(require_basic_auth)) -> dict[str, object]:
    """Return the orchestrator model picker choices for the UI."""
    return {"default": _DEFAULT_MODEL, "choices": _ALLOWED_MODELS}


@app.post("/chat")
async def chat(
    request: ChatRequest,
    _user: str = Depends(require_basic_auth),
) -> JSONResponse:
    model = _resolve_model(request.model)
    with trace_span("zava.chat", query=request.query):
        result = await run_query(
            request.query,
            manager_model=model,
            conversation_id=request.conversation_id,
        )
    return JSONResponse(
        {
            "final_answer": result.final_answer,
            "plan": result.plan,
            "transcripts": result.transcripts,
            "events": result.events,
        }
    )


@app.post("/chat/stream")
async def chat_stream(
    request: ChatRequest,
    _user: str = Depends(require_basic_auth),
) -> StreamingResponse:
    """Server-Sent Events feed of orchestrator activity.

    The browser opens this with ``fetch`` + a streaming reader and renders
    each event (manager plan, per-agent transcript, final answer) as it
    arrives, giving a live "what is happening" view of the multi-agent
    workflow.
    """

    async def event_source():
        model = _resolve_model(request.model)
        with trace_span("zava.chat.stream", query=request.query):
            async for payload in stream_query(
                request.query,
                manager_model=model,
                conversation_id=request.conversation_id,
            ):
                yield f"data: {json.dumps(payload)}\n\n"

    return StreamingResponse(
        event_source(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )


@app.get("/", response_class=HTMLResponse)
def index(_user: str = Depends(require_basic_auth)) -> HTMLResponse:
    # Read on every request so edits to chat.html show up without a server
    # restart. Also disable browser caching so a plain reload picks them up.
    html = _CHAT_HTML_PATH.read_text(encoding="utf-8")
    return HTMLResponse(
        html,
        headers={"Cache-Control": "no-store, no-cache, must-revalidate, max-age=0"},
    )

"""FastAPI chat application for the Pepsico multi-agent assistant."""

from __future__ import annotations

from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.responses import HTMLResponse, JSONResponse
from pydantic import BaseModel, Field

from src.common.observability import configure_observability, trace_span
from src.orchestrator.magentic_router import run_query

load_dotenv()

app = FastAPI(title="Pepsico AI Agents Workshop", version="1.0.0")
observability_enabled = configure_observability(app)
_CHAT_HTML = (Path(__file__).with_name("chat.html")).read_text(encoding="utf-8")


class ChatRequest(BaseModel):
    query: str = Field(..., min_length=1, examples=["What is our PTO policy?"])


@app.get("/health")
def health() -> dict[str, object]:
    return {"status": "ok", "observability_enabled": observability_enabled}


@app.post("/chat")
async def chat(request: ChatRequest) -> JSONResponse:
    with trace_span("pepsico.chat", query=request.query):
        result = await run_query(request.query)
    return JSONResponse(
        {
            "final_answer": result.final_answer,
            "plan": result.plan,
            "transcripts": result.transcripts,
            "events": result.events,
        }
    )


@app.get("/", response_class=HTMLResponse)
def index() -> str:
    return _CHAT_HTML

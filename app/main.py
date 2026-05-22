from __future__ import annotations

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from pydantic import BaseModel, Field

from .agents import LocalOrchestrator
from .observability import configure_observability, trace_span

load_dotenv()

app = FastAPI(title="AI Agents Workshop", version="0.1.0")
orchestrator = LocalOrchestrator()
observability_enabled = configure_observability(app)


class ChatRequest(BaseModel):
    query: str = Field(..., min_length=1, examples=["What is the PTO policy?"])
    agent: str = Field("auto", examples=["auto"])


@app.get("/health")
def health() -> dict[str, bool | str]:
    return {"status": "ok", "observability_enabled": observability_enabled}


@app.get("/agents")
def agents() -> list[dict[str, str]]:
    return [
        {"name": agent.name, "description": agent.description}
        for agent in orchestrator.agents
    ]


@app.post("/chat")
def chat(request: ChatRequest) -> dict[str, object]:
    with trace_span("api.agent_query", agent=request.agent, query=request.query):
        if request.agent == "auto":
            result = orchestrator.answer(request.query)
        else:
            result = orchestrator.answer_with_agent(request.agent, request.query)
    return {
        "route": result.route,
        "answer": result.answer,
        "confidence": round(result.confidence, 2),
        "sources": result.sources,
        "considered_agents": result.considered_agents,
    }


@app.get("/", response_class=HTMLResponse)
def index() -> str:
    return """
<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>AI Agents Workshop</title>
  <style>
    body { font-family: Segoe UI, Arial, sans-serif; margin: 0; background: #f7f7f7; color: #1f1f1f; }
    main { max-width: 920px; margin: 0 auto; padding: 32px 20px; }
    h1 { font-size: 32px; margin-bottom: 8px; }
    form, section { background: white; border: 1px solid #ddd; border-radius: 8px; padding: 20px; margin-top: 20px; }
    label { display: block; font-weight: 600; margin-bottom: 8px; }
    textarea, select { width: 100%; box-sizing: border-box; padding: 10px; border: 1px solid #bbb; border-radius: 4px; font: inherit; }
    textarea { min-height: 92px; resize: vertical; }
    button { margin-top: 12px; padding: 10px 14px; border: 0; border-radius: 4px; background: #2563eb; color: white; font-weight: 600; cursor: pointer; }
    pre { white-space: pre-wrap; background: #111827; color: #f9fafb; padding: 16px; border-radius: 6px; overflow: auto; }
  </style>
</head>
<body>
  <main>
    <h1>AI Agents Workshop</h1>
    <p>Ask a question and let the local orchestrator route it to HR, Products, or Marketing.</p>
    <form id="chat-form">
      <label for="agent">Agent</label>
      <select id="agent">
        <option value="auto">Auto route</option>
        <option value="hr">HR</option>
        <option value="products">Products</option>
        <option value="marketing">Marketing</option>
      </select>
      <label for="query" style="margin-top: 16px;">Question</label>
      <textarea id="query">What is the PTO policy?</textarea>
      <button type="submit">Ask</button>
    </form>
    <section>
      <h2>Response</h2>
      <pre id="response">Ready.</pre>
    </section>
  </main>
  <script>
    const form = document.querySelector('#chat-form');
    const response = document.querySelector('#response');
    form.addEventListener('submit', async (event) => {
      event.preventDefault();
      response.textContent = 'Thinking...';
      const result = await fetch('/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          agent: document.querySelector('#agent').value,
          query: document.querySelector('#query').value
        })
      });
      response.textContent = JSON.stringify(await result.json(), null, 2);
    });
  </script>
</body>
</html>
"""

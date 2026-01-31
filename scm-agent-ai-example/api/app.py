from typing import List, Optional

from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel, Field

from agent.engine import run_agent
from config import index_exists
from index_loader import ensure_indexes


app = FastAPI(title="SCM Agent API", version="1.0.0")


class QueryRequest(BaseModel):
    query: str = Field(..., min_length=1)
    top_k: int = Field(3, ge=1, le=10)


class SourceItem(BaseModel):
    chunk_id: str
    source: str
    score: float
    text: str
    page_text: str = ""


class QueryResponse(BaseModel):
    answer: str
    sources: List[SourceItem]
    confidence: float
    domain: str
    formatted: str


@app.on_event("startup")
def _startup() -> None:
    ensure_indexes()


@app.get("/health")
def health() -> dict:
    return {
        "status": "ok",
        "indexes": {
            "supply": index_exists("supply"),
            "demand": index_exists("demand"),
        },
    }


@app.get("/", response_class=HTMLResponse)
def root() -> str:
    return """
<!doctype html>
<html lang="en">
  <head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <title>SCM Agent Demo</title>
    <style>
      body { font-family: system-ui, sans-serif; margin: 32px; }
      .row { margin-bottom: 16px; }
      textarea { width: 100%; height: 120px; }
      pre { background: #f6f8fa; padding: 12px; white-space: pre-wrap; }
      .status { font-size: 14px; color: #444; }
    </style>
  </head>
  <body>
    <h1>SCM Agent Demo</h1>
    <div class="status" id="health">Checking health...</div>
    <div class="row">
      <label for="query">Query</label>
      <textarea id="query" placeholder="Ask about demand forecasting, supplier risk, logistics, etc."></textarea>
    </div>
    <div class="row">
      <label for="topk">Top K</label>
      <input id="topk" type="number" min="1" max="10" value="3" />
      <button id="run">Run</button>
    </div>
    <h3>Answer</h3>
    <pre id="answer"></pre>
    <h3>Sources</h3>
    <pre id="sources"></pre>
    <script>
      const healthEl = document.getElementById('health');
      fetch('/health')
        .then(r => r.json())
        .then(data => {
          healthEl.textContent = `Health: ${data.status} | supply=${data.indexes.supply} demand=${data.indexes.demand}`;
        })
        .catch(() => {
          healthEl.textContent = 'Health: unavailable';
        });

      document.getElementById('run').addEventListener('click', async () => {
        const query = document.getElementById('query').value.trim();
        const topK = parseInt(document.getElementById('topk').value, 10) || 3;
        if (!query) return;
        const res = await fetch('/query', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ query, top_k: topK })
        });
        if (!res.ok) {
          document.getElementById('answer').textContent = 'Request failed.';
          document.getElementById('sources').textContent = '';
          return;
        }
        const data = await res.json();
        document.getElementById('answer').textContent = data.answer || '';
        document.getElementById('sources').textContent = JSON.stringify(data.sources || [], null, 2);
      });
    </script>
  </body>
</html>
"""


@app.post("/query", response_model=QueryResponse)
def query(payload: QueryRequest) -> QueryResponse:
    if not payload.query.strip():
        raise HTTPException(status_code=400, detail="Query must not be empty.")
    result = run_agent(payload.query, top_k=payload.top_k)
    return QueryResponse(**result)

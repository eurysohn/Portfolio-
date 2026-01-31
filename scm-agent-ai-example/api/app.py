from pathlib import Path
from typing import List, Optional

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from agent.engine import run_agent
from config import index_exists
from index_loader import ensure_indexes


app = FastAPI(title="SCM Agent API", version="1.0.0")
BASE_DIR = Path(__file__).resolve().parents[1]
FRONTEND_DIR = BASE_DIR / "frontend"
if FRONTEND_DIR.exists():
    app.mount("/static", StaticFiles(directory=FRONTEND_DIR), name="static")


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
def root() -> HTMLResponse:
    index_path = FRONTEND_DIR / "index.html"
    if index_path.exists():
        return FileResponse(index_path)
    return HTMLResponse("<h3>Frontend missing. Build the frontend assets.</h3>")


@app.post("/query", response_model=QueryResponse)
def query(payload: QueryRequest) -> QueryResponse:
    if not payload.query.strip():
        raise HTTPException(status_code=400, detail="Query must not be empty.")
    result = run_agent(payload.query, top_k=payload.top_k)
    return QueryResponse(**result)

import json
import os
import time
import uuid
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

from fastapi import FastAPI, Form, Query, Request, Header, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from .agent import AgentConfig, Text2SQLAgent
from .schema import SchemaCache, introspect_schema, schema_as_dict

app = FastAPI(title="Enterprise Text-to-SQL Agent")
agent = Text2SQLAgent(AgentConfig(db_url="sqlite:///data/app.db"))
_sessions: Dict[str, Dict[str, Any]] = {}
_session_runs: Dict[str, List[Dict[str, Any]]] = {}
_rate_limit: Dict[str, Dict[str, Any]] = {}  # Now stores count + timestamp
_rate_limit_max = int(os.getenv("RATE_LIMIT_MAX", "3"))
_rate_limit_window_hours = int(os.getenv("RATE_LIMIT_WINDOW_HOURS", "24"))
_demo_mode = os.getenv("DEMO_MODE", "true").lower() == "true"
_api_token = os.getenv("API_TOKEN", None)  # Optional token for bypassing rate limits
_client_cookie_name = "t2s_client_id"

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://enterprise-text-to-sql-agent-ui.fly.dev",
        "http://localhost:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class AskRequest(BaseModel):
    question: str
    scope: str = "default"


@app.get("/healthz")
def healthz() -> dict:
    return {"status": "ok"}


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}


@app.get("/")
def root() -> dict:
    return {
        "message": "Enterprise Text-to-SQL Agent",
        "demo_mode": _demo_mode,
        "rate_limit": {
            "max_requests": _rate_limit_max,
            "window_hours": _rate_limit_window_hours,
            "message": f"Demo is limited to {_rate_limit_max} requests per {_rate_limit_window_hours} hours per person"
        },
        "endpoints": {
            "healthz": "/healthz",
            "schema": "/schema",
            "ask": "/ask",
        },
    }


@app.get("/schema")
def get_schema() -> dict:
    snapshot = introspect_schema("sqlite:///data/app.db", SchemaCache())
    return schema_as_dict(snapshot)


@app.post("/ask")
def ask(
    request: AskRequest, 
    http_request: Request,
    authorization: Optional[str] = Header(None)
) -> dict:
    client_id, set_cookie = _ensure_client_id(http_request)
    _enforce_rate_limit(http_request, client_id, authorization)
    response_payload = agent.ask(request.question, scope=request.scope)
    if set_cookie:
        response = JSONResponse(content=response_payload)
        response.set_cookie(_client_cookie_name, client_id, httponly=True, samesite="lax")
        return response
    return response_payload


@app.get("/agents")
def get_agents() -> List[Dict[str, Any]]:
    return [
        {
            "id": "text2sql-agent",
            "name": "Enterprise Text-to-SQL Agent",
            "db_id": "sqlite",
            "model": {"name": "rule-based", "model": "deterministic", "provider": "local"},
        }
    ]


@app.get("/teams")
def get_teams() -> List[Dict[str, Any]]:
    return []


@app.get("/sessions")
def get_sessions(
    type: str = Query("agent"),
    component_id: Optional[str] = Query(None),
    db_id: Optional[str] = Query(None),
) -> Dict[str, Any]:
    data = list(_sessions.values())
    return {
        "data": data,
        "meta": {
            "page": 1,
            "limit": len(data),
            "total_pages": 1,
            "total_count": len(data),
        },
    }


@app.get("/sessions/{session_id}/runs")
def get_session_runs(
    session_id: str,
    type: str = Query("agent"),
    db_id: Optional[str] = Query(None),
) -> List[Dict[str, Any]]:
    return _session_runs.get(session_id, [])


@app.delete("/sessions/{session_id}")
def delete_session(session_id: str, db_id: Optional[str] = Query(None)) -> Dict[str, Any]:
    _sessions.pop(session_id, None)
    return {"deleted": True}


@app.post("/agents/{agent_id}/runs")
def run_agent(
    agent_id: str,
    http_request: Request,
    message: str = Form(...),
    stream: str = Form("true"),
    session_id: Optional[str] = Form(None),
    authorization: Optional[str] = Header(None)
) -> StreamingResponse:
    client_id, set_cookie = _ensure_client_id(http_request)
    _enforce_rate_limit(http_request, client_id, authorization)
    run_id = str(uuid.uuid4())
    created_at = int(time.time())
    session_id = session_id or str(uuid.uuid4())

    if session_id not in _sessions:
        _sessions[session_id] = {
            "session_id": session_id,
            "session_name": message,
            "created_at": created_at,
            "updated_at": created_at,
        }
    else:
        _sessions[session_id]["updated_at"] = created_at

    response_payload = agent.ask(message, scope="default")
    reasoning_steps = response_payload.get("extra_data", {}).get("reasoning_steps", [])
    result_payload = response_payload.get("result") or {}
    summary = result_payload.get("summary") or {}
    
    # Get the formatted summary or create a good default
    if isinstance(summary, dict):
        summary_text = summary.get("summary", "Result calculated")
    else:
        summary_text = str(summary) if summary else "Result calculated"
    
    # If it's a clarification or error message, use that instead
    if response_payload.get("clarification"):
        summary_text = response_payload.get("clarification")
    elif response_payload.get("message"):
        summary_text = response_payload.get("message")
    
    rationale = response_payload.get("rationale") or "Rule-based KPI template."
    sql_text = response_payload.get("sql") or "-- no sql generated --"

    def _format_thinking() -> str:
        if not reasoning_steps:
            return "1. **Scope check**\n2. **Schema grounding**\n3. **SQL generation**\n4. **Validation**\n5. **Execution**"
        lines: List[str] = []
        for idx, step in enumerate(reasoning_steps, start=1):
            title = step.get("title", "Step")
            result = step.get("result", "OK")
            lines.append(f"{idx}. **{title}**: {result}")
        return "\n".join(lines)

    formatted_summary = (
        f"### 📊 Answer\n\n"
        f"**{summary_text}**\n\n"
        f"---\n\n"
        f"### 💡 How this was calculated\n\n"
        f"{rationale}\n\n"
        f"---\n\n"
        f"### 🔍 SQL Query\n\n"
        f"```sql\n{sql_text}\n```\n\n"
        f"---\n\n"
        f"### 🧠 Thinking Process\n\n"
        f"{_format_thinking()}"
    )

    def _emit(payload: Dict[str, Any]) -> str:
        return json.dumps(payload) + "\n"

    def event_stream():
        yield _emit(
            {
                "event": "RunStarted",
                "content_type": "application/json",
                "created_at": created_at,
                "run_id": run_id,
                "agent_id": agent_id,
                "session_id": session_id,
            }
        )
        yield _emit(
            {
                "event": "ReasoningStarted",
                "content_type": "application/json",
                "created_at": created_at + 1,
                "run_id": run_id,
                "agent_id": agent_id,
                "session_id": session_id,
            }
        )
        yield _emit(
            {
                "event": "ReasoningStep",
                "content_type": "application/json",
                "created_at": created_at + 2,
                "run_id": run_id,
                "agent_id": agent_id,
                "session_id": session_id,
                "extra_data": {"reasoning_steps": reasoning_steps},
            }
        )
        yield _emit(
            {
                "event": "ReasoningCompleted",
                "content_type": "application/json",
                "created_at": created_at + 3,
                "run_id": run_id,
                "agent_id": agent_id,
                "session_id": session_id,
                "extra_data": {"reasoning_steps": reasoning_steps},
            }
        )
        yield _emit(
            {
                "event": "RunContent",
                "content": formatted_summary,
                "content_type": "text/plain",
                "created_at": created_at + 4,
                "run_id": run_id,
                "agent_id": agent_id,
                "session_id": session_id,
                "extra_data": {"reasoning_steps": reasoning_steps},
            }
        )
        yield _emit(
            {
                "event": "RunCompleted",
                "content": response_payload,
                "content_type": "application/json",
                "created_at": created_at + 5,
                "run_id": run_id,
                "agent_id": agent_id,
                "session_id": session_id,
                "extra_data": {"reasoning_steps": reasoning_steps},
            }
        )

    response = StreamingResponse(event_stream(), media_type="application/json")
    if set_cookie:
        response.set_cookie(_client_cookie_name, client_id, httponly=True, samesite="lax")
    _session_runs.setdefault(session_id, []).append(
        {
            "run_input": message,
            "content": formatted_summary,
            "created_at": created_at,
            "tools": [],
            "extra_data": {"reasoning_steps": reasoning_steps},
        }
    )
    return response


def _ensure_client_id(request: Request) -> tuple[str, bool]:
    existing = request.cookies.get(_client_cookie_name)
    if existing:
        return existing, False
    return str(uuid.uuid4()), True


def _enforce_rate_limit(request: Request, client_id: str, authorization: Optional[str] = None) -> None:
    # Bypass rate limit if valid API token provided
    if _api_token and authorization:
        token = authorization.replace("Bearer ", "")
        if token == _api_token:
            return
    
    # Demo mode: enforce strict rate limits
    if not _demo_mode:
        return
    
    client_ip = request.client.host if request.client else "unknown"
    key = f"{client_ip}:{client_id}"
    
    now = datetime.now()
    
    # Get or initialize rate limit data
    if key not in _rate_limit:
        _rate_limit[key] = {"count": 0, "window_start": now}
    
    rate_data = _rate_limit[key]
    window_start = rate_data["window_start"]
    
    # Reset if window has expired
    if now - window_start > timedelta(hours=_rate_limit_window_hours):
        _rate_limit[key] = {"count": 0, "window_start": now}
        rate_data = _rate_limit[key]
    
    # Check limit
    if rate_data["count"] >= _rate_limit_max:
        time_remaining = (_rate_limit_window_hours * 3600) - (now - window_start).total_seconds()
        hours_remaining = int(time_remaining / 3600)
        minutes_remaining = int((time_remaining % 3600) / 60)
        raise RateLimitExceeded(hours_remaining, minutes_remaining)
    
    # Increment counter
    _rate_limit[key]["count"] += 1


class RateLimitExceeded(Exception):
    def __init__(self, hours_remaining: int, minutes_remaining: int):
        self.hours_remaining = hours_remaining
        self.minutes_remaining = minutes_remaining


@app.exception_handler(RateLimitExceeded)
def _rate_limit_handler(request: Request, exc: RateLimitExceeded) -> JSONResponse:
    return JSONResponse(
        status_code=429,
        content={
            "detail": "I'm sorry, but to protect usage I've limited to 3 times per person.",
            "limit": _rate_limit_max,
        },
    )

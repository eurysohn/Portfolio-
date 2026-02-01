import json
import time
import uuid
from typing import Any, Dict, List, Optional

from fastapi import FastAPI, Form, Query, Request
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
_rate_limit: Dict[str, int] = {}
_rate_limit_max = 3
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
def ask(request: AskRequest, http_request: Request) -> dict:
    client_id, set_cookie = _ensure_client_id(http_request)
    _enforce_rate_limit(http_request, client_id)
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
) -> StreamingResponse:
    client_id, set_cookie = _ensure_client_id(http_request)
    _enforce_rate_limit(http_request, client_id)
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
    summary_text = (
        summary.get("summary")
        or response_payload.get("message")
        or response_payload.get("clarification")
        or "OK"
    )
    rationale = response_payload.get("rationale") or "Rule-based KPI template."
    sql_text = response_payload.get("sql") or "-- no sql generated --"
    reasoning_steps = response_payload.get("extra_data", {}).get("reasoning_steps", [])

    def _format_thinking() -> str:
        if not reasoning_steps:
            return "- STEP 1: Scope check\n- STEP 2: Schema grounding\n- STEP 3: SQL generation\n- STEP 4: Validation\n- STEP 5: Execution"
        lines: List[str] = []
        for idx, step in enumerate(reasoning_steps, start=1):
            title = step.get("title", "Step")
            result = step.get("result", "OK")
            lines.append(f"- STEP {idx}: {title} — {result}")
        return "\n".join(lines)

    formatted_summary = (
        f"**{summary_text}**\n\n"
        f"*Source: {rationale}*\n\n"
        f"*SQL*\n"
        f"```sql\n{sql_text}\n```\n\n"
        f"*Thinking*\n"
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


def _enforce_rate_limit(request: Request, client_id: str) -> None:
    client_ip = request.client.host if request.client else "unknown"
    key = f"{client_ip}:{client_id}"
    current = _rate_limit.get(key, 0)
    if current >= _rate_limit_max:
        raise RateLimitExceeded()
    _rate_limit[key] = current + 1


class RateLimitExceeded(Exception):
    pass


@app.exception_handler(RateLimitExceeded)
def _rate_limit_handler(request: Request, exc: RateLimitExceeded) -> JSONResponse:
    return JSONResponse(
        status_code=429,
        content={
            "detail": "I'm sorry, but to protect usage I've limited to 3 times per person.",
            "limit": _rate_limit_max,
        },
    )

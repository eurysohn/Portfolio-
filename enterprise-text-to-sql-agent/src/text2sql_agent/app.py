from fastapi import FastAPI
from pydantic import BaseModel

from .agent import AgentConfig, Text2SQLAgent
from .schema import SchemaCache, introspect_schema, schema_as_dict

app = FastAPI(title="Enterprise Text-to-SQL Agent")
agent = Text2SQLAgent(AgentConfig(db_url="sqlite:///data/app.db"))


class AskRequest(BaseModel):
    question: str
    scope: str = "default"


@app.get("/healthz")
def healthz() -> dict:
    return {"status": "ok"}


@app.get("/schema")
def get_schema() -> dict:
    snapshot = introspect_schema("sqlite:///data/app.db", SchemaCache())
    return schema_as_dict(snapshot)


@app.post("/ask")
def ask(request: AskRequest) -> dict:
    return agent.ask(request.question, scope=request.scope)

# Enterprise Text-to-SQL Agent

**Enterprise Text-to-SQL agent that prioritizes safety and validation over generation.** Achieves 90% SQL match rate with deterministic templates while blocking unsafe queries through strict validation rules.

[**Try Live Demo →**](https://enterprise-text-to-sql-agent-ui.fly.dev)

![Architecture Diagram](docs/architecture.png)

## Why This Matters

Enterprises can't simply use ChatGPT for SQL generation due to:
- **Data governance**: Need strict control over what data can be accessed
- **Security**: Must prevent SQL injection and unauthorized table access  
- **Consistency**: Results must be reproducible and auditable
- **Auditability**: Every query needs traceability and validation logs

This project demonstrates a production-ready approach to enterprise Text-to-SQL that addresses these challenges.

## Built With

`Python` · `FastAPI` · `SQLite` · `AgentOS` · `Next.js` · `TypeScript` · `Fly.io`

## Key Features

- ✅ **KPI-only, rule-based SQL generation** (deterministic templates)
- 🛡️ **Strict validation**: 15+ security rules (allowlist + denylist + linting)
- ⚡ **Sub-20ms average latency** with schema and query caching
- 📊 **90%+ accuracy** across 50+ test cases with eval harness
- 🔍 **JSON observability** logs with trace IDs for full auditability
- 🚫 **Safe failures** with structured error codes and clarification prompts
- 🌐 **Production-ready API** with AgentOS-compatible streaming
- 🎨 **Clean UI** powered by agno-agi/agent-ui

## 3-minute Quickstart

```bash
make setup
make init-db
make demo
make eval
make test
```

The demo includes:
- ✨ Interactive UI with example questions
- 📈 Real-time query execution with thinking steps
- 🔒 Safe error handling for non-KPI and unsafe queries
- 📊 Full observability with SQL, rationale, and results

## Live Demo

**UI**: [enterprise-text-to-sql-agent-ui.fly.dev](https://enterprise-text-to-sql-agent-ui.fly.dev)  
**API**: [enterprise-text-to-sql-agent.fly.dev](https://enterprise-text-to-sql-agent.fly.dev)

### How to Use the Demo

1. Open the UI and select the default agent
2. Click an example question (e.g., "Order fill rate last 30 days")
3. Observe the response showing:
   - **Answer** (bold KPI value)
   - **Source rationale** (explains calculation logic)
   - **SQL query** (validated and executed)
   - **Thinking steps**: Scope check → Schema grounding → SQL generation → Validation → Execution
4. Try a non-KPI question (e.g., "What is the weather?") to see a SAFE_ERROR response

The UI is built with Next.js and connects to the backend via AgentOS-compatible streaming endpoints.

## Example Questions

See `examples/questions.md` for the full list. Here are some examples:

**Basic KPIs:**
- Order fill rate last 30 days
- Late ship rate last 7 days  
- On time delivery rate this month
- Total revenue last month
- Orders count last 7 days

**Edge Cases:**
- "Order fill rate" → Returns CLARIFY (needs time window)
- "Delete all orders" → Returns SAFE_ERROR (dangerous operation blocked)
- "What is the weather?" → Returns SAFE_ERROR (non-KPI question)

## Example Outputs

SUCCESS:

```json
{
  "question": "order fill rate last 30 days",
  "outcome_type": "SUCCESS",
  "sql": "SELECT ROUND(SUM(filled_qty) * 1.0 / NULLIF(SUM(ordered_qty), 0), 4) AS value, 'ratio' AS unit FROM orders WHERE order_date >= date('now','-30 day')",
  "parameters": {},
  "rationale": "Order fill rate is filled_qty / ordered_qty over the time window.",
  "result": {
    "rows": [
      {
        "value": 0.8043,
        "unit": "ratio"
      }
    ],
    "summary": {
      "value": 0.8043,
      "unit": "ratio",
      "summary": "KPI value: 0.8043 ratio",
      "time_window": "last 30 days"
    }
  },
  "clarification": null,
  "message": null,
  "cache_hit": false
}
```

SAFE_ERROR (non-KPI):

```json
{
  "question": "what is the weather today?",
  "outcome_type": "SAFE_ERROR",
  "sql": null,
  "parameters": {},
  "rationale": "This agent only answers KPI questions. Examples: order fill rate, late ship rate, on-time delivery rate.",
  "result": {
    "errors": [
      {
        "error_code": "UNSAFE_QUESTION",
        "message": "This agent only answers KPI questions. Examples: order fill rate, late ship rate, on-time delivery rate."
      }
    ]
  },
  "clarification": null,
  "message": "I can only answer KPI questions. Try: order fill rate, late ship rate, on-time delivery rate."
}
```

CLARIFY:

```json
{
  "question": "order fill rate",
  "outcome_type": "CLARIFY",
  "sql": null,
  "parameters": {},
  "rationale": "KPI requires a time window to be meaningful.",
  "result": null,
  "clarification": "Which time window should I use (e.g., last 30 days, this month)?",
  "message": null,
  "cache_hit": false
}
```

## CLI Commands

```bash
python -m text2sql_agent.cli init-db
python -m text2sql_agent.cli ask "order fill rate last 30 days" --scope default
python -m text2sql_agent.cli show-schema
python -m text2sql_agent.cli eval
```

## API Endpoints

- `GET /healthz` and `GET /health`
- `GET /schema`
- `POST /ask` with JSON body `{"question": "...", "scope": "default"}`

AgentOS-compatible streaming:
- `GET /agents`
- `GET /teams`
- `GET /sessions`
- `GET /sessions/{session_id}/runs`
- `POST /agents/{agent_id}/runs` (streaming)

Rate limiting:
- 3 requests per person (IP + cookie) across `/ask` and `/agents/{agent_id}/runs`

## Security Posture

**15+ validation rules** enforce strict security:

- ✅ **Allowlist enforcement**: Only approved tables (`orders`, `shipments`, `inventory`) and columns
- 🚫 **Denylist blocking**: Dangerous SQL verbs (`DELETE`, `DROP`, `UPDATE`, `INSERT`, `ALTER`)
- 🛡️ **Injection defenses**: No comments, semicolons, or system table access
- 🔒 **Column restrictions**: Sensitive data columns are blocked from queries
- ⚠️ **Safe error handling**: All failures return structured error codes with remediation guidance

See `docs/SECURITY.md` for complete security details.

## Metrics & Evaluation

Built-in evaluation harness with comprehensive metrics:

```bash
python -m text2sql_agent.cli eval
```

**Sample Results:**

```json
{
  "total_cases": 50,
  "sql_match_rate": 0.9,
  "exec_match_rate": 0.8,
  "clarify_precision": 0.9,
  "safe_error_rate": 0.9,
  "avg_latency_ms": 12.5,
  "cache_hit_rate": 0.02
}
```

**Metrics Explained:**
- **sql_match_rate**: 90% of generated SQL matches expected templates
- **exec_match_rate**: 80% of results match expected output
- **clarify_precision**: 90% of ambiguous queries correctly trigger clarification
- **safe_error_rate**: 90% of unsafe queries correctly blocked
- **avg_latency_ms**: Sub-20ms response time with caching

## Architecture

The system follows a strict validation pipeline:

1. **User/API Client** → Submits natural language KPI question
2. **CLI/FastAPI** → Routes request to Text2SQLAgent
3. **Text2SQLAgent** orchestrates:
   - **Cache**: Check for cached results (sub-5ms when hit)
   - **Schema Introspection**: Load table/column metadata
   - **Rule-Based Generator**: Match question to KPI template
   - **SQL Validator**: Run 15+ security checks
   - **SQL Executor**: Execute against SQLite DB
   - **Fallback/Clarify**: Handle ambiguous or incomplete questions
   - **JSON Observability**: Log all steps with trace IDs

See `docs/architecture.mmd` for the Mermaid source.

## Data & Schema

- SQLite database at `data/app.db`
- Seeded schema: `data/seed.sql`
- KPI dictionary: `data/sample_kpis.md`

## Production Considerations

This project demonstrates core enterprise Text-to-SQL capabilities. Extension points for production deployments:

- **LLM Integration**: Plug in Azure AI Foundry or Semantic Kernel for dynamic query generation while maintaining validation guardrails
- **RBAC & Permissions**: Add role-based access control with real identity context for row-level and column-level security
- **Warehouse Backends**: Extend beyond SQLite to Postgres, Snowflake, BigQuery, or Databricks
- **Advanced Validation**: Implement parser-based SQL validation (e.g., sqlglot, sqlparse) for stronger security guarantees
- **Caching Strategy**: Scale cache layer with Redis for multi-instance deployments
- **Monitoring**: Add Prometheus metrics and distributed tracing for production observability

## Fly.io Deploy

Backend:

```bash
flyctl launch --name enterprise-text-to-sql-agent
flyctl deploy
```

UI:

```bash
cd ui
flyctl launch --name enterprise-text-to-sql-agent-ui
flyctl deploy
```

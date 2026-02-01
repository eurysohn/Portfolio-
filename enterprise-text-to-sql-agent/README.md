# enterprise-text-to-sql-agent

In enterprise Text-to-SQL, safety/validation/permissions matter more than generation.

This repository demonstrates an offline, enterprise-grade Text-to-SQL assistant focused on validation, guardrails, and evaluation. SQL generation is deterministic and rule-based by default, with an optional LLM adapter stubbed for future use.

![Architecture](docs/architecture.png)

## 3-minute Quickstart

```bash
make setup
make init-db
make demo
make eval
make test
```

## What It Does

- Deterministic KPI generation (rule-based templates)
- Strict validation: allowlist + denylist + linting rules
- Safe failures with structured error codes
- Schema cache and query cache
- Evaluation harness with SQL match + exec match metrics
- JSON observability logs with trace IDs

## Example Questions

See `examples/questions.md` for 10 sample questions.

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

## Security Posture

- Allowlist/denylist enforcement (tables, columns, dangerous verbs)
- SQL injection defenses (no comments, no semicolons, no system tables)
- Safe errors with remediation guidance
- Column restrictions for sensitive data

See `docs/SECURITY.md` for details.

## Metrics & Evaluation

Run:

```bash
python -m text2sql_agent.cli eval
```

Sample output:

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

## Architecture

Mermaid source: `docs/architecture.mmd`

## Data & Schema

- SQLite database at `data/app.db`
- Seeded schema: `data/seed.sql`
- KPI dictionary: `data/sample_kpis.md`

## Tradeoffs & Next steps

- Plug in Azure AI Foundry or Semantic Kernel for generation.
- Add RBAC and real identity context for permissioning.
- Expand to warehouse backends (Postgres, Snowflake).
- Add parser-based SQL validation for stronger security.

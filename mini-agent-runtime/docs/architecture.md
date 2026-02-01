# Architecture

The runtime is designed as a small but production-style agent platform:

- `runtime/` orchestrates routing, tool execution, guardrails, memory/state, and idempotency.
- `agents/` define workflows and action plans.
- `tools/` implement generic tool calls with a shared interface.
- `observability/` provides JSON logs and trace event storage.
- `eval/` runs a golden set with a rule-based judge.

## Component view

```mermaid
flowchart LR
    subgraph Client
        UI[Frontend UI]
        CLI[CLI / API]
    end

    subgraph Runtime
        Router[Router]
        Engine[AgentRuntime]
        Memory[Session Memory]
        Idem[Idempotency Store]
        Exec[Tool Executor]
        Obs[Logs + Traces]
    end

    subgraph Agents
        RunbookAgent[Runbook Agent]
        DataAgent[Data Query Agent]
        EscalationAgent[Escalation Agent]
    end

    subgraph Tools
        RunbookTool[Runbook Lookup]
        DataTool[Metrics Query]
        HttpTool[HTTP Tool]
        DbTool[DB Tool]
        NotifyTool[Notify Oncall]
    end

    UI -->|ticket| Engine
    CLI -->|ticket| Engine
    Engine --> Router
    Engine --> Memory
    Engine --> Idem
    Router --> Agents
    Agents --> Exec
    Exec --> Tools
    Engine --> Obs
```

## Run sequence (happy path)

```mermaid
sequenceDiagram
    participant Client
    participant Engine
    participant Router
    participant Agent
    participant Executor
    participant Tool
    participant Trace

    Client->>Engine: ticket + correlation_id
    Engine->>Router: decide_route()
    Router->>Engine: route + confidence
    Engine->>Agent: build_plan()
    Agent->>Executor: tool_calls
    Executor->>Tool: invoke()
    Tool->>Executor: tool_result
    Executor->>Engine: tool_results
    Engine->>Trace: record run_complete
    Engine->>Client: AgentResult
```

## Observability + state

```mermaid
flowchart TB
    Engine -->|structured logs| Logs[(JSON Logs)]
    Engine -->|trace events| Traces[(Trace Store)]
    Engine -->|session entries| Memory[(Memory Store)]
    Engine -->|idempotency cache| Idem[(Idempotency Store)]
```

Traces are stored in memory and also persisted to `logs/traces.jsonl` so you can
inspect a run later using:

```
python -m runtime.cli show-trace <run_id>
```

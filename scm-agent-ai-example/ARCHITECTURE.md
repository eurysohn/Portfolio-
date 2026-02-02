# Architecture

## System Overview
The SCM Agent is built following a modular, tool-augmented agent pattern.

```mermaid
graph TD
    Client[Client / Tool] --> API[FastAPI /api/main.py]
    API --> Middleware[Correlation ID Middleware]
    Middleware --> AgentEngine[Agent Engine /agent/engine.py]
    AgentEngine --> Router[Intent Router /agent/router.py]
    AgentEngine --> Dictionary[Dictionary Expansion]
    AgentEngine --> RAG[RAG Retrieval]
    AgentEngine --> DataQuery[Structured Data Query]
    AgentEngine --> WebFallback[Web Search Fallback]
    AgentEngine --> Trace[Workflow Trace /app/trace_schema.py]
    
    subgraph Tools
        CALC[Calculators]
        DICT[Dictionary Lookup]
        RAGSEARCH[RAG Search]
        WEB[Web Fallback]
        DATA[Data Query]
    end
    
    Router --> |Determine Intent| AgentEngine
    AgentEngine --> |Execute| CALC
    AgentEngine --> |Execute| DICT
    AgentEngine --> |Execute| RAGSEARCH
    AgentEngine --> |Execute| DATA
    AgentEngine --> |Execute| WEB
```

## Core Components
- **FastAPI Layer**: Handles request/response, middleware for logging, and endpoint routing.
- **Intent Routing**: A deterministic (keyword) or probabilistic (LLM) router that classifies user queries into domains (Calculation, Definition, Planning).
- **Tool Orchestration**: The engine coordinates dictionary expansion → internal RAG → data query → web fallback.
- **Configuration**: Managed via `pydantic-settings` for robust environment variable validation.
- **Observability**: Correlation IDs on every request and a minimal `/metrics` endpoint for Prometheus scraping.
- **Workflow Trace**: Every response includes route/tool decisions and retrieval sources.

## Deployment Info
- **Containerization**: Multi-stage Docker build optimized for size and security (non-root user).
- **Platform**: Fly.io for global edge deployment with automated health checks.

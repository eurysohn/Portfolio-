# Architecture

## System Overview
The SCM Agent is built following a modular, tool-augmented agent pattern.

```mermaid
graph TD
    Client[Client / Tool] --> API[FastAPI /api/main.py]
    API --> Middleware[Correlation ID Middleware]
    Middleware --> AgentEngine[Agent Engine /agent/engine.py]
    AgentEngine --> Router[Intent Router /agent/router.py]
    AgentEngine --> Tools[Tools Directory /tools/]
    
    subgraph Tools
        CALC[Calculators]
        DICT[Dictionary Lookup]
        RAG[RAG Search]
        WEB[Web Fallback]
    end
    
    Router --> |Determine Intent| AgentEngine
    AgentEngine --> |Execute| CALC
    AgentEngine --> |Execute| DICT
    AgentEngine --> |Execute| RAG
```

## Core Components
- **FastAPI Layer**: Handles request/response, middleware for logging, and endpoint routing.
- **Intent Routing**: A deterministic (keyword) or probabilistic (LLM) router that classifies user queries into domains (Calculation, Definition, Planning).
- **Tool Orchestration**: The engine coordinates multiple tools. If internal knowledge (RAG/Dict) fails, it can fall back to web search.
- **Configuration**: Managed via `pydantic-settings` for robust environment variable validation.

## Deployment Info
- **Containerization**: Multi-stage Docker build optimized for size and security (non-root user).
- **Platform**: Fly.io for global edge deployment with automated health checks.

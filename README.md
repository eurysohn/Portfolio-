# Hi 👋 I'm Eury Sohn  
**Forward-Deployed Engineer | AI Systems & Enterprise Agent Deployment**

I build and deploy production-grade AI systems in real enterprise environments.

Currently working at **LG CNS** as an **AI Agent Deployment Owner / Product Consultant**, leading end-to-end delivery of enterprise-scale SCM AI Agents that automate real operational workflows across ERP, data pipelines, and business systems.

My focus is not just model performance, but **deployment reliability, system integration, observability, and business adoption**.

---
 
## What I Do

- Design and deploy production AI agent systems integrated with enterprise ERP and analytics pipelines  
- Build Text-to-SQL and LLM-powered operational analytics pipelines for business users  
- Own end-to-end delivery lifecycle: architecture, deployment, monitoring, incident response  
- Work directly with stakeholders to translate ambiguous business requirements into working systems  
- Operate AI systems at scale (10,000+ users, 1,000 concurrent users)

---

## Current Role

**LG CNS — AI Agent Deployment Owner / SCM Consultant**

- Led production rollout of SCM Expert AI Agent replacing enterprise CSR workflows  
- Built unified AI operational interface combining ERP transactional data and domain knowledge  
- Designed deployment automation and data orchestration pipelines  
- Operated enterprise platform automating 100+ daily CSR requests with 87% automation rate  
- Managed production incidents, privacy risk mitigation, rollback and redeployment strategies  

---

## Education

- M.S. Information (Data Science), University of Wisconsin–Madison (GPA 3.8/4.0)  
- B.S. Creative Technology Management, Yonsei University (GPA 4.15/4.3)  

---

## Tech Stack

**Languages & Data**  
Python, SQL, TypeScript, MongoDB, Pandas, NumPy  

**AI / ML**  
LLM Pipelines, NLP, Text-to-SQL, RAG (TF-IDF, Embedding Retrieval), Scikit-learn, PyTorch  

**Systems & DevOps**  
FastAPI, Docker, Redis, Prometheus, Grafana, GitHub Actions CI/CD, Fly.io, Vercel  

**Analytics**  
Tableau, PowerBI, Looker  

---

## Featured Projects

### Mini Agent Runtime
Production-style agent execution engine for an "Enterprise Ops Copilot" that routes support tickets, calls tools, and handles failures with production-grade reliability.

**Key Features:**
- Agent orchestration and routing across runbook/data/escalation workflows
- Tool interface with mocked HTTP + DB tools plus retries, timeouts, and circuit breakers
- Memory/state per session (rolling context for recent runs)
- Observability with structured JSON logs, audit events, and trace storage
- Evaluation harness with golden set and offline judge
- Security basics: PII redaction and prompt injection guardrails
- React + TypeScript frontend with session history panel

**Tech:** Python, FastAPI, React, TypeScript, Docker, GitHub Actions CI

[View Repository →](https://github.com/eurysohn/Portfolio-/tree/main/mini-agent-runtime)

---

### Enterprise Text-to-SQL Agent
Enterprise-grade Text-to-SQL assistant focused on validation, guardrails, and evaluation — because in enterprise, safety/validation/permissions matter more than generation.

**Key Features:**
- Deterministic KPI generation (rule-based templates)
- Strict validation: allowlist + denylist + SQL injection defenses
- Safe failures with structured error codes and clarification prompts
- Schema cache and query cache for performance
- Evaluation harness with SQL match + exec match metrics
- JSON observability logs with trace IDs
- React + TypeScript chat UI with streaming responses

**Tech:** Python, FastAPI, SQLite, Docker, GitHub Actions CI, Fly.io deployment

[View Repository →](https://github.com/eurysohn/Portfolio-/tree/main/enterprise-text-to-sql-agent)

---

### SCM Agent AI Example
Production-style SCM enterprise agent with RAG, terminology dictionary, intent routing, tool orchestration, and evaluation — demonstrating real-world SCM domain expertise.

**Key Features:**
- TF-IDF RAG over SCM source documents (supply/demand indexes)
- Terminology dictionary with synonyms and fuzzy lookup
- Intent routing across SCM domains (supply, demand, general)
- Tool orchestration (RAG + dictionary + calculators + web fallback)
- Structured JSONL logging and golden-set evaluation
- Data pipeline: URL download → document processing → vector index build
- FastAPI service with demo UI

**Tech:** Python, FastAPI, TF-IDF Vector Search, Docker, S3 (optional index storage)

[View Repository →](https://github.com/eurysohn/Portfolio-/tree/main/scm-agent-ai-example)

---

### FastAPI Deployment Pipeline
Production-ready FastAPI deployment pipeline demonstrating DevOps best practices with enterprise-grade CI/CD, observability, and security.

**Key Features:**
- Full CI/CD pipeline: Lint → Security Scan → Test → Build → Deploy
- Observability stack: Prometheus metrics + Grafana dashboards + structured logging
- Security scanning: Bandit (SAST), Safety (dependency audit), Trivy (container scan)
- Kubernetes-ready health checks (`/healthz`, `/readyz`)
- Request ID tracing for distributed systems
- Load testing with Locust
- 70%+ code coverage threshold

**Tech:** Python, FastAPI, Docker, Redis, Prometheus, Grafana, GitHub Actions, GHCR

[View Repository →](https://github.com/eurysohn/Portfolio-/tree/main/FastAI-Deployment-Pipeline)

---

## Contact

LinkedIn: https://www.linkedin.com/in/eury-sohn  
Email: eurysohn@gmail.com  

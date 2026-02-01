# mini-agent-runtime

Production-style agent runtime demo for an "Enterprise Ops Copilot" that routes support
tickets, calls tools, emits structured logs + traces, evaluates against a golden set, and
handles failures with retries/timeouts/circuit breakers.

“Designed for production constraints: retries, timeouts, idempotency, audit logs”

## What this repo demonstrates

- Agent orchestration and routing across runbook/data/escalation workflows
- Tool interface with mocked HTTP + DB tools plus retries, timeouts, and circuit breakers
- Memory/state per session (rolling context for recent runs)
- Observability with structured JSON logs, audit events, and trace storage
- Evaluation harness with golden set and offline judge
- Security basics: PII redaction and prompt injection guardrails

## Architecture

![Architecture](docs/arch.png)

Detailed Mermaid diagrams live in `docs/architecture.md`.

## 3-minute quickstart

```bash
make setup
make run
```

Run the demo and evaluation:

```bash
make demo
make test
```

Inspect a trace after running:

```bash
python -m runtime.cli show-trace <run_id>
```

## Demo GIF

![Screen Recording 2026-02-01 at 8](https://github.com/user-attachments/assets/44eb9c74-9d23-44be-af6e-8f1b45f4ee2d)

## Frontend demo

Run the UI + API server:

```bash
PORT=8001 make ui
```

Then open `http://localhost:8001` to submit tickets and inspect traces.

## TypeScript frontend (agent-ui inspired)

This Vite + React UI keeps the left history panel and a simple runtime console.

Start the API server (port 8001 default):

```bash
PORT=8001 make ui
```

Start the TypeScript UI:

```bash
cd frontend-ts
npm install
npm run dev
```

Then open `http://localhost:5173`. If your API runs on another port, set
`VITE_API_BASE` (for example `VITE_API_BASE=http://localhost:9000 npm run dev`).

## Public demo deployment (recommended)

For a shareable demo, deploy the API and frontend separately:

- API: Render / Railway / Fly.io (run `python3 -m runtime.api`)
- Frontend: Vercel (set `VITE_API_BASE` to your API URL)

Quick local sharing for reviewers:

```bash
# expose API on a public URL
ngrok http 8001

# run frontend with the public API base
VITE_API_BASE=https://<your-ngrok-subdomain>.ngrok.app npm run dev
```

## Platform fit notes

- Microsoft: this runtime keeps a clean tool/router boundary so Azure AI Foundry or
  Semantic Kernel adapters can be plugged into `runtime/llm.py` and the agent layer.
- Sendbird: customer-specific tool bindings, failures, and observability are centralized
  in the runtime + tool registry, making multi-tenant ops flows easy to manage.

## Demo GIF placeholder

Record a short CLI walkthrough and save it as `docs/demo.gif`. Update this section with:

```
![Demo](docs/demo.gif)
```

## Tradeoffs and next steps

- This baseline is deterministic and rule-based for local runs without API keys.
- Tools are in-memory mocks; replace with real services or data stores as needed.
- To plug in Azure AI Foundry or Semantic Kernel later, add an LLM adapter in
  `runtime/llm.py` and swap the router/agent implementations to call it.

## Commands

- `make setup` - install dependencies
- `make run` - run interactive CLI
- `make demo` - run sample tickets
- `make ui` - run web UI + API server
- `make test` - run unit tests
- `make lint` - run ruff
- `python -m eval.run_eval` - run golden set evaluation

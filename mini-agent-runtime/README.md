# mini-agent-runtime

Production-style agent runtime demo for an "Enterprise Ops Copilot" that routes support
tickets, calls tools, emits structured logs + traces, evaluates against a golden set, and
handles failures with retries/timeouts/circuit breakers.

## What this repo demonstrates

- Agent orchestration and routing across runbook/data/escalation workflows
- Generic tool interface with retries, timeouts, and circuit breakers
- Observability with structured JSON logs and trace events
- Evaluation harness with golden set and offline judge
- Security basics: PII redaction and prompt injection guardrails

## Architecture

![Architecture](docs/arch.png)

More details in `docs/architecture.md`.

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


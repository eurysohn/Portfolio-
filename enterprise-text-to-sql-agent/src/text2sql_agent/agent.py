from dataclasses import asdict, dataclass
from typing import Any, Dict, Optional

from .cache import FileCache, cache_key
from .executor import SQLExecutor, summarize_kpi
from .fallback import (
    clarification_response,
    escalation_message,
    safe_error_response,
    too_many_rows_response,
)
from .generator import GenerationResult, RuleBasedGenerator
from .observability import Observability, Timer, TraceContext
from .schema import SchemaCache, introspect_schema, schema_as_dict
from .validator import SQLValidator


@dataclass
class AgentConfig:
    db_url: str = "sqlite:///data/app.db"
    max_rows: int = 200
    allow_union: bool = False
    table_allowlist: Optional[set[str]] = None
    column_denylist: Optional[set[str]] = None


class Text2SQLAgent:
    def __init__(
        self,
        config: AgentConfig | None = None,
        *,
        cache: FileCache | None = None,
        observability: Observability | None = None,
    ) -> None:
        self.config = config or AgentConfig()
        self.cache = cache or FileCache()
        self.schema_cache = SchemaCache()
        self.observability = observability or Observability()
        self.generator = RuleBasedGenerator()
        self.executor = SQLExecutor(self.config.db_url)

    def ask(self, question: str, scope: str = "default") -> Dict[str, Any]:
        ctx = TraceContext()
        timer = Timer()

        schema_snapshot = introspect_schema(self.config.db_url, self.schema_cache)
        schema_dict = schema_as_dict(schema_snapshot)
        reasoning_steps: list[Dict[str, Any]] = [
            {
                "title": "Scope check",
                "action": "Identify KPI intent",
                "result": "Pending",
                "reasoning": "Only KPI questions are allowed.",
            },
            {
                "title": "Schema grounding",
                "action": "Load schema cache",
                "result": "Schema snapshot available",
                "reasoning": "Schema is used to constrain valid tables/columns.",
            },
            {
                "title": "SQL generation",
                "action": "Apply KPI template",
                "result": "Pending",
                "reasoning": "Rule-based KPI templates generate deterministic SQL.",
            },
            {
                "title": "Validation",
                "action": "Apply allow/deny rules",
                "result": "Pending",
                "reasoning": "Guardrails prevent unsafe SQL access.",
            },
            {
                "title": "Execution",
                "action": "Run on SQLite",
                "result": "Pending",
                "reasoning": "Execute and summarize KPI result.",
            },
        ]
        cache_id = cache_key(question, schema_snapshot.schema_hash, scope)
        cached = self.cache.get(cache_id)
        if cached:
            cached.response["cache_hit"] = True
            self.observability.log_event(
                ctx,
                level="info",
                stage="cache",
                message="Cache hit",
                cache_hit=True,
                outcome_type=cached.response.get("outcome_type"),
                latency_ms=timer.elapsed_ms(),
            )
            return cached.response

        self.observability.log_event(
            ctx, level="info", stage="cache", message="Cache miss", cache_hit=False
        )

        generation = self.generator.generate(question, schema_dict)
        reasoning_steps[0]["result"] = (
            "KPI intent detected" if generation.outcome_type != "SAFE_ERROR" else "Non-KPI"
        )
        reasoning_steps[2]["result"] = generation.sql or "No SQL generated"
        if generation.outcome_type == "CLARIFY":
            response = self._build_response(
                generation,
                question,
                ctx,
                outcome_type="CLARIFY",
                result=None,
                sql=None,
                cache_hit=False,
                latency_ms=timer.elapsed_ms(),
                reasoning_steps=reasoning_steps,
            )
            self.cache.set(cache_id, response)
            return response

        if generation.outcome_type != "SUCCESS" or not generation.sql:
            error_code = (
                "UNSAFE_QUESTION"
                if generation.outcome_type == "SAFE_ERROR"
                else "GENERATION_FAILED"
            )
            response = self._safe_error(
                ctx,
                timer,
                [{"error_code": error_code, "message": generation.rationale}],
                question,
                generation,
                reasoning_steps,
            )
            response["cache_hit"] = False
            self.cache.set(cache_id, response)
            return response

        validator = SQLValidator(
            table_allowlist=self.config.table_allowlist
            or set(schema_dict.keys()),
            column_denylist=self.config.column_denylist
            or {"customer_email", "ssn"},
            allow_union=self.config.allow_union,
        )
        validation = validator.validate(generation.sql, schema_dict)
        if not validation.passed:
            reasoning_steps[3]["result"] = "Blocked"
            response = self._safe_error(
                ctx,
                timer,
                [asdict(error) for error in validation.errors],
                question,
                generation,
                reasoning_steps,
            )
            response["cache_hit"] = False
            self.cache.set(cache_id, response)
            return response
        reasoning_steps[3]["result"] = "Validated"

        exec_result = self.executor.run(generation.sql, generation.parameters)
        if exec_result.row_count > self.config.max_rows:
            reasoning_steps[4]["result"] = f"Too many rows: {exec_result.row_count}"
            fallback = too_many_rows_response(exec_result.row_count)
            response = self._build_response(
                generation,
                question,
                ctx,
                outcome_type=fallback.outcome_type,
                result=fallback.details,
                sql=generation.sql,
                message=fallback.message,
                cache_hit=False,
                latency_ms=timer.elapsed_ms(),
                reasoning_steps=reasoning_steps,
            )
            self.cache.set(cache_id, response)
            return response

        reasoning_steps[4]["result"] = f"Executed rows: {exec_result.row_count}"
        summary = summarize_kpi(exec_result.rows, generation.time_window)
        response = self._build_response(
            generation,
            question,
            ctx,
            outcome_type="SUCCESS",
            result={
                "rows": exec_result.rows,
                "summary": summary,
            },
            sql=generation.sql,
            cache_hit=False,
            latency_ms=timer.elapsed_ms(),
            reasoning_steps=reasoning_steps,
        )
        self.cache.set(cache_id, response)
        return response

    def _safe_error(
        self,
        ctx: TraceContext,
        timer: Timer,
        errors: list[Dict[str, str]],
        question: str,
        generation: GenerationResult,
        reasoning_steps: list[Dict[str, Any]],
    ) -> Dict[str, Any]:
        fallback = safe_error_response(errors)
        response = self._build_response(
            generation,
            question,
            ctx,
            outcome_type=fallback.outcome_type,
            result=fallback.details,
            sql=generation.sql,
            message=fallback.message,
            latency_ms=timer.elapsed_ms(),
            reasoning_steps=reasoning_steps,
        )
        response["escalation"] = escalation_message()
        self.observability.log_event(
            ctx,
            level="warning",
            stage="validation",
            message="Validation failed",
            validation_passed=False,
            outcome_type=fallback.outcome_type,
            latency_ms=timer.elapsed_ms(),
        )
        return response

    def _build_response(
        self,
        generation: GenerationResult,
        question: str,
        ctx: TraceContext,
        *,
        outcome_type: str,
        result: Optional[Dict[str, Any]],
        sql: Optional[str],
        message: Optional[str] = None,
        cache_hit: Optional[bool] = None,
        latency_ms: Optional[float] = None,
        reasoning_steps: Optional[list[Dict[str, Any]]] = None,
    ) -> Dict[str, Any]:
        response = {
            "question": question,
            "outcome_type": outcome_type,
            "sql": sql,
            "parameters": generation.parameters,
            "rationale": generation.rationale,
            "result": result,
            "clarification": generation.clarification,
            "message": message,
            "trace_id": ctx.trace_id,
            "run_id": ctx.run_id,
        }
        if reasoning_steps is not None:
            response["extra_data"] = {"reasoning_steps": reasoning_steps}
        if cache_hit is not None:
            response["cache_hit"] = cache_hit
        self.observability.log_event(
            ctx,
            level="info",
            stage="response",
            message="Response generated",
            validation_passed=outcome_type == "SUCCESS",
            outcome_type=outcome_type,
            latency_ms=latency_ms,
        )
        return response

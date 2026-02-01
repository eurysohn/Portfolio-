from dataclasses import dataclass
from typing import Any, Dict, List


@dataclass
class FallbackResponse:
    outcome_type: str
    message: str
    details: Dict[str, Any]


def clarification_response(question: str, clarification: str) -> FallbackResponse:
    return FallbackResponse(
        outcome_type="CLARIFY",
        message=clarification,
        details={"question": question},
    )


def safe_error_response(errors: List[Dict[str, str]]) -> FallbackResponse:
    return FallbackResponse(
        outcome_type="SAFE_ERROR",
        message="The request could not be executed safely.",
        details={"errors": errors},
    )


def too_many_rows_response(row_count: int) -> FallbackResponse:
    return FallbackResponse(
        outcome_type="SAFE_ERROR",
        message="The query returned too many rows. Please narrow the scope.",
        details={"row_count": row_count},
    )


def escalation_message() -> str:
    return (
        "Escalation template: Please open a data request ticket with the business KPI "
        "name, desired timeframe, and business unit."
    )

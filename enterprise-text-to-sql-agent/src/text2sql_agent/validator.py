import re
from dataclasses import dataclass
from typing import Dict, List, Optional, Set, Tuple


@dataclass
class ValidationError:
    error_code: str
    message: str
    remediation: str


@dataclass
class ValidationResult:
    passed: bool
    errors: List[ValidationError]


class SQLValidator:
    def __init__(
        self,
        *,
        table_allowlist: Set[str],
        column_denylist: Set[str],
        allow_union: bool = False,
    ) -> None:
        self.table_allowlist = {table.lower() for table in table_allowlist}
        self.column_denylist = {column.lower() for column in column_denylist}
        self.allow_union = allow_union

    def validate(self, sql: str, schema_dict: Dict[str, Dict[str, str]]) -> ValidationResult:
        errors: List[ValidationError] = []
        normalized = sql.strip().lower()

        if not normalized.startswith("select "):
            errors.append(
                ValidationError(
                    "ONLY_SELECT_ALLOWED",
                    "Only SELECT statements are allowed.",
                    "Rephrase the question as a read-only KPI request.",
                )
            )
        if ";" in normalized:
            errors.append(
                ValidationError(
                    "SEMICOLON_NOT_ALLOWED",
                    "Semicolons are not allowed in queries.",
                    "Remove semicolons and run a single statement.",
                )
            )
        if "--" in normalized or "/*" in normalized:
            errors.append(
                ValidationError(
                    "COMMENTS_NOT_ALLOWED",
                    "SQL comments are not allowed.",
                    "Remove comments from the query.",
                )
            )
        if re.search(r"\b(drop|delete|update|insert|alter|pragma|attach)\b", normalized):
            errors.append(
                ValidationError(
                    "DANGEROUS_STATEMENT",
                    "Potentially destructive SQL detected.",
                    "Use a read-only KPI request.",
                )
            )
        if "sqlite_master" in normalized:
            errors.append(
                ValidationError(
                    "SYSTEM_TABLE_ACCESS",
                    "Access to sqlite_master is not allowed.",
                    "Query approved business tables only.",
                )
            )
        if not self.allow_union and " union " in normalized:
            errors.append(
                ValidationError(
                    "UNION_NOT_ALLOWED",
                    "UNION queries are not allowed.",
                    "Avoid UNION and request a single KPI.",
                )
            )
        if re.search(r"\bselect\s+\*\b", normalized):
            errors.append(
                ValidationError(
                    "SELECT_STAR_NOT_ALLOWED",
                    "SELECT * is not allowed.",
                    "Select specific columns or use KPI templates.",
                )
            )
        if " cross join " in normalized:
            errors.append(
                ValidationError(
                    "CROSS_JOIN_NOT_ALLOWED",
                    "CROSS JOIN is not allowed.",
                    "Use explicit join conditions only.",
                )
            )

        table_refs, column_refs = _extract_refs(normalized)
        for table in table_refs:
            if table not in self.table_allowlist:
                errors.append(
                    ValidationError(
                        "TABLE_NOT_ALLOWED",
                        f"Table '{table}' is not in the allowlist.",
                        "Request only approved KPI tables.",
                    )
                )
        for column in column_refs:
            if column in self.column_denylist:
                errors.append(
                    ValidationError(
                        "COLUMN_NOT_ALLOWED",
                        f"Column '{column}' is restricted.",
                        "Remove sensitive fields from the request.",
                    )
                )

        lint_errors = self._lint(sql)
        errors.extend(lint_errors)
        return ValidationResult(passed=len(errors) == 0, errors=errors)

    def _lint(self, sql: str) -> List[ValidationError]:
        normalized = sql.strip().lower()
        if " limit " not in normalized and not _is_aggregate_query(normalized):
            return [
                ValidationError(
                    "LIMIT_RECOMMENDED",
                    "Broad queries should include a LIMIT.",
                    "Add a LIMIT clause or request a KPI summary.",
                )
            ]
        return []


def _extract_refs(sql: str) -> Tuple[Set[str], Set[str]]:
    table_refs: Set[str] = set()
    column_refs: Set[str] = set()
    for match in re.finditer(r"\bfrom\s+([a-zA-Z_][a-zA-Z0-9_]*)", sql):
        table_refs.add(match.group(1))
    for match in re.finditer(r"\bjoin\s+([a-zA-Z_][a-zA-Z0-9_]*)", sql):
        table_refs.add(match.group(1))
    for match in re.finditer(r"\bselect\s+(.*?)\s+from\b", sql):
        select_body = match.group(1)
        parts = re.split(r"\s*,\s*", select_body)
        for part in parts:
            token = part.strip().split(" ")[0]
            if "." in token:
                token = token.split(".")[-1]
            if token and token not in {"count(*)", "sum(*)"}:
                column_refs.add(token)
    return table_refs, column_refs


def _is_aggregate_query(sql: str) -> bool:
    return any(func in sql for func in ["count(", "sum(", "avg(", "min(", "max("])

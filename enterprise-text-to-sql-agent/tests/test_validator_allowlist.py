from text2sql_agent.validator import SQLValidator


def test_validator_allows_select_on_allowlist():
    validator = SQLValidator(table_allowlist={"orders"}, column_denylist=set())
    result = validator.validate(
        "SELECT COUNT(*) AS value FROM orders WHERE order_id > 0",
        {"orders": {"order_id": "INTEGER"}},
    )
    assert result.passed is True


def test_validator_blocks_unknown_table():
    validator = SQLValidator(table_allowlist={"orders"}, column_denylist=set())
    result = validator.validate(
        "SELECT COUNT(*) AS value FROM secret_table",
        {"orders": {"order_id": "INTEGER"}},
    )
    assert result.passed is False
    assert any(error.error_code == "TABLE_NOT_ALLOWED" for error in result.errors)

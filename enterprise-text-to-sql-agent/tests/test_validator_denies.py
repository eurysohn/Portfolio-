from text2sql_agent.validator import SQLValidator


def test_validator_blocks_semicolon():
    validator = SQLValidator(table_allowlist={"orders"}, column_denylist=set())
    result = validator.validate(
        "SELECT COUNT(*) AS value FROM orders; DROP TABLE orders",
        {"orders": {"order_id": "INTEGER"}},
    )
    assert result.passed is False
    assert any(error.error_code == "SEMICOLON_NOT_ALLOWED" for error in result.errors)


def test_validator_blocks_select_star():
    validator = SQLValidator(table_allowlist={"orders"}, column_denylist=set())
    result = validator.validate(
        "SELECT * FROM orders",
        {"orders": {"order_id": "INTEGER"}},
    )
    assert result.passed is False
    assert any(error.error_code == "SELECT_STAR_NOT_ALLOWED" for error in result.errors)


def test_validator_blocks_cross_join():
    validator = SQLValidator(table_allowlist={"orders", "shipments"}, column_denylist=set())
    result = validator.validate(
        "SELECT orders.order_id FROM orders CROSS JOIN shipments",
        {"orders": {"order_id": "INTEGER"}, "shipments": {"shipment_id": "INTEGER"}},
    )
    assert result.passed is False
    assert any(error.error_code == "CROSS_JOIN_NOT_ALLOWED" for error in result.errors)

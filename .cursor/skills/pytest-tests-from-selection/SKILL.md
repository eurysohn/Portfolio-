---
name: pytest-tests-from-selection
description: Generate pytest test file from selected code, covering happy path, edge cases, and mocking external APIs/DBs. Use when the user asks for pytest tests, test generation, or when code is selected for test creation.
---

# Pytest Tests From Selection

## Quick Start
1. Read the selected code and its module context.
2. Determine the correct `tests/` path and naming based on existing conventions.
3. Write a minimal happy-path test first, then add edge cases and mocks.

## Requirements
- **Happy path:** Valid inputs return expected outputs.
- **Edge cases:** Include empty lists, `None`, and zero integers when relevant.
- **Mocking:** External API/DB calls must be mocked with `unittest.mock` or `pytest-mock`.
- **No real network:** Ensure tests cannot perform real network calls.

## Workflow
1. Identify public functions/classes to test and the expected behavior.
2. Scan for external dependencies (HTTP clients, DB drivers, SDKs) and locate call sites.
3. Use existing fixtures in `conftest.py` if present; add new fixtures only if needed.
4. Prefer `pytest-mock`'s `mocker` fixture when available; otherwise use `unittest.mock.patch`.
5. Add TODOs for follow-up improvements such as integration tests or richer fixtures.

## Minimal Test Template
```python
import pytest

from <module> import <target>


def test_<target>_happy_path():
    result = <target>(<valid_input>)
    assert result == <expected_output>


@pytest.mark.parametrize(
    "input_value",
    [
        <empty_list>,
        None,
        0,
    ],
)
def test_<target>_edge_cases(input_value):
    # Adjust assertions based on expected behavior (error vs default result).
    result = <target>(input_value)
    assert result == <expected_output_or_exception>


def test_<target>_mocks_external_call(mocker):
    mocked = mocker.patch("<module>.<external_call>")
    mocked.return_value = <mocked_response>
    result = <target>(<valid_input>)
    assert result == <expected_output>
    mocked.assert_called_once()
```

## Additional Resources
- If project has testing guidelines, read them first and follow the same style.

# Security Posture

This repository prioritizes safety over generation quality. The following controls are enforced:

- Allowlist: only approved tables are accessible; only SELECT statements allowed.
- Denylist patterns: DROP/DELETE/UPDATE/INSERT/ALTER/PRAGMA/ATTACH, comments, semicolons, UNION, sqlite_master access.
- Column restrictions: sensitive columns (e.g., customer_email, ssn) are blocked.
- SQL linting: SELECT * and CROSS JOIN are prohibited; broad queries require LIMIT.
- Safe errors: validation failures return structured error codes and remediation tips.
- Prompt injection defense: unsafe keywords in the question trigger SAFE_ERROR before SQL generation.

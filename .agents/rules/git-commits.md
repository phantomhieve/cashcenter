# Git Commit Guidelines

## Policy:
1. **Always Have a Proper Commit Message**:
   - Write clear, concise, imperative subject lines (e.g., `feat: add multi-stage DAG market intelligence app`, `fix: resolve MultipleObjectsReturned when fetching l_r_no`).
   - Keep the first line under 72 characters.
   - Include a body paragraph whenever the context, rationale, or trade-offs are not obvious from the subject line.
   - Match the established repository commit history style (`feat: ...`, `fix: ...`, `refactor: ...`).

2. **Pre-commit Verification**:
   - Always run pre-commit verification before finalizing changes: secret scanning, lint, and Django checks (`django/manage.py check`).
   - Verify that `.codegraph` is synchronized before committing.

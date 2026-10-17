#!/usr/bin/env bash
set -eo pipefail

echo "==> Running CashCenter pre-commit checks..."

# 1. Prevent secret / sensitive files from being staged
FORBIDDEN_PATTERNS='(\.env$|\.env\.local$|\.key\.json$|id_rsa|\.pem$|\.pfx$)'
STAGED_FILES=$(git diff --cached --name-only)

for file in $STAGED_FILES; do
    if echo "$file" | grep -Eq "$FORBIDDEN_PATTERNS"; then
        echo "❌ ERROR: Attempting to commit forbidden secret/credential file: $file"
        echo "Please unstage this file immediately before committing."
        exit 1
    fi
done

# 2. Check for merge conflict markers
if git diff --cached -- ':!scripts/pre-commit.sh' ':!.github/workflows/ci.yml' -S"<<<<<<< " --quiet; then
    :
else
    echo "❌ ERROR: Unresolved merge conflict markers detected in staged changes."
    exit 1
fi

# 3. Synchronize CodeGraph knowledge index if installed
if command -v codegraph >/dev/null 2>&1; then
    echo "==> Synchronizing CodeGraph..."
    codegraph sync >/dev/null 2>&1 || true
elif [ -x "/opt/homebrew/bin/codegraph" ]; then
    echo "==> Synchronizing CodeGraph..."
    /opt/homebrew/bin/codegraph sync >/dev/null 2>&1 || true
fi

# 4. Django system check
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
DJANGO_DIR="$REPO_ROOT/django"

if [ -f "$DJANGO_DIR/.venv/bin/python" ]; then
    echo "==> Running Django system check..."
    (cd "$DJANGO_DIR" && .venv/bin/python manage.py check --fail-level ERROR)
fi

echo "✅ All pre-commit checks passed successfully!"
exit 0

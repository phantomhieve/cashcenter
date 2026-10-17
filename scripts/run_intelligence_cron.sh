#!/usr/bin/env bash
# ==============================================================================
# CashCenter — 30-Day Automated Market Intelligence Cron Runner
#
# Intended to be run periodically (e.g. daily at 02:00 AM) via crontab or systemd.
# Automatically evaluates whether 30 days have elapsed since each user's last run,
# and executes the Gemini AI DAG market intelligence analysis for eligible shops.
# ==============================================================================

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
DJANGO_DIR="$REPO_ROOT/django"
LOG_DIR="${LOG_DIR:-$REPO_ROOT/logs}"

mkdir -p "$LOG_DIR"
LOG_FILE="$LOG_DIR/intelligence_cron.log"

echo "[$(date -u '+%Y-%m-%d %H:%M:%S UTC')] ==> Initiating Market Intelligence 30-day cron check..." | tee -a "$LOG_FILE"

cd "$DJANGO_DIR"

# Locate virtual environment Python
PYTHON_BIN=""
if [[ -f "$DJANGO_DIR/.venv/bin/python" ]]; then
    PYTHON_BIN="$DJANGO_DIR/.venv/bin/python"
elif [[ -f "$REPO_ROOT/.venv/bin/python" ]]; then
    PYTHON_BIN="$REPO_ROOT/.venv/bin/python"
elif command -v python3 >/dev/null 2>&1; then
    PYTHON_BIN="$(command -v python3)"
else
    echo "❌ ERROR: No Python interpreter found for Django environment." | tee -a "$LOG_FILE"
    exit 1
fi

# Run the Django management command, passing through any custom flags (e.g. --force, --dry-run)
"$PYTHON_BIN" manage.py run_intelligence_cron "$@" 2>&1 | tee -a "$LOG_FILE"

EXIT_CODE="${PIPESTATUS[0]}"

if [[ "$EXIT_CODE" -eq 0 ]]; then
    echo "[$(date -u '+%Y-%m-%d %H:%M:%S UTC')] ✅ Market Intelligence cron job completed successfully." | tee -a "$LOG_FILE"
else
    echo "[$(date -u '+%Y-%m-%d %H:%M:%S UTC')] ❌ Market Intelligence cron job exited with code $EXIT_CODE." | tee -a "$LOG_FILE"
fi

exit "$EXIT_CODE"

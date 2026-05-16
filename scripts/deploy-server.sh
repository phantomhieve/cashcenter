#!/usr/bin/env bash
# Deploy over SSH + rsync. See .github/DEPLOY-SECRETS.md for CI variables.

set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
HOST="${DEPLOY_HOST:?set DEPLOY_HOST}"
USER="${DEPLOY_USER:-cashcenter-deploy}"
SSH_PORT="${DEPLOY_SSH_PORT:-22}"
REMOTE_APP="${DEPLOY_APP_DIR:?set DEPLOY_APP_DIR}"
REMOTE_DJANGO="${REMOTE_APP}/django"
ACTIVATE_SCRIPT=/usr/local/sbin/cashcenter-deploy-activate.sh

SSH_OPTS=(-o StrictHostKeyChecking=accept-new -p "$SSH_PORT")
if [[ -n "${SSH_KEY_FILE:-}" ]]; then
  SSH_OPTS+=(-i "$SSH_KEY_FILE")
fi
RSYNC_SSH="ssh ${SSH_OPTS[*]}"
# Deploy user is group-writer, not owner — do not preserve times/owner (rsync -a utime fails).
RSYNC_FLAGS=(-rlvz --no-times --omit-dir-times)

echo "==> Deploy as ${USER}@${HOST}"

rsync "${RSYNC_FLAGS[@]}" \
  -e "$RSYNC_SSH" \
  --exclude '.env' \
  --exclude '.env.server' \
  --exclude '__pycache__/' \
  --exclude '*.pyc' \
  --exclude 'staticfiles/' \
  --exclude '.venv/' \
  --exclude 'seed_data.py' \
  --exclude 'generate_legacy_data.py' \
  --exclude 'static/library/vendor/' \
  --exclude 'static/library/fonts/' \
  --exclude 'static/library/css/util.css' \
  "${ROOT}/django/" "${USER}@${HOST}:${REMOTE_DJANGO}/"

rsync "${RSYNC_FLAGS[@]}" -e "$RSYNC_SSH" "${ROOT}/requirements.txt" "${USER}@${HOST}:${REMOTE_APP}/requirements.txt"

if [[ "${DEPLOY_USE_LEGACY_ACTIVATE:-0}" == "1" ]]; then
  ssh "${SSH_OPTS[@]}" "${USER}@${HOST}" bash -s <<REMOTE
set -euo pipefail
cd ${REMOTE_APP}
.venv/bin/pip install -q -r requirements.txt
cd django
../.venv/bin/python manage.py migrate --noinput
../.venv/bin/python manage.py collectstatic --noinput
sudo systemctl restart gunicorn-cashcenter.service
sleep 2
sudo systemctl is-active --quiet gunicorn-cashcenter.service
REMOTE
else
  ssh "${SSH_OPTS[@]}" "${USER}@${HOST}" "sudo ${ACTIVATE_SCRIPT}"
fi

if [[ -n "${DEPLOY_HEALTHCHECK_URL:-}" ]] && command -v curl >/dev/null; then
  code=$(curl -s -o /dev/null -w '%{http_code}' --max-time 15 -L "${DEPLOY_HEALTHCHECK_URL}" || echo "000")
  echo "==> Health check HTTP ${code}"
fi

echo "==> Deploy complete"

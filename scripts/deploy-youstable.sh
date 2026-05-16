#!/usr/bin/env bash
# Deploy cashcenter to server (production).
#
# CI (GitHub Actions / GitLab CI): dedicated user cashcenter-deploy
#   DEPLOY_SSH_PRIVATE_KEY → secrets
#   DEPLOY_USER=cashcenter-deploy (default)
#
# Manual admin deploy (optional, existing atul access):
#   DEPLOY_USER=atul SSH_KEY_FILE=~/.ssh/admin_ssh_key ./scripts/deploy-server.sh
#
# Env: DEPLOY_HOST, DEPLOY_USER, DEPLOY_SSH_PORT, SSH_KEY_FILE

set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
HOST="${DEPLOY_HOST:?set DEPLOY_HOST}"
USER="${DEPLOY_USER:-}"
USER="${USER:-cashcenter-deploy}"
SSH_PORT="${DEPLOY_SSH_PORT:-22}"
REMOTE_APP=/home/YOUR_APP_USER/cash-center
REMOTE_DJANGO="${REMOTE_APP}/django"
ACTIVATE_SCRIPT=/usr/local/sbin/cashcenter-deploy-activate.sh

SSH_OPTS=(-o StrictHostKeyChecking=accept-new -p "$SSH_PORT")
if [[ -n "${SSH_KEY_FILE:-}" ]]; then
  SSH_OPTS+=(-i "$SSH_KEY_FILE")
fi
RSYNC_SSH="ssh ${SSH_OPTS[*]}"

echo "==> Deploy as ${USER}@${HOST}"

echo "==> Sync django/ → ${REMOTE_DJANGO}"
rsync -avz \
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

echo "==> Sync requirements.txt"
rsync -avz -e "$RSYNC_SSH" "${ROOT}/requirements.txt" "${USER}@${HOST}:${REMOTE_APP}/requirements.txt"

echo "==> Activate on server (migrate, collectstatic, restart)"
if [[ "$USER" == "cashcenter-deploy" ]]; then
  ssh "${SSH_OPTS[@]}" "${USER}@${HOST}" "sudo ${ACTIVATE_SCRIPT}"
else
  # Legacy: full shell as atul (manual only)
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
echo "gunicorn-cashcenter: active"
REMOTE
fi

echo "==> Smoke check https://your-site.example/"
if command -v curl >/dev/null; then
  code=$(curl -s -o /dev/null -w '%{http_code}' --max-time 15 -L https://your-site.example/ || echo "000")
  echo "HTTP ${code} (expect 200 or 302)"
fi

echo "==> Deploy complete"

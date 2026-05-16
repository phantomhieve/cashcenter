#!/usr/bin/env bash
# Deploy cashcenter to server (production).
# Used by GitHub Actions and optionally from a developer machine:
#   DEPLOY_HOST=YOUR_DEPLOY_HOST DEPLOY_USER=atul ./scripts/deploy-server.sh
#
# GitHub secrets: DEPLOY_SSH_PRIVATE_KEY, DEPLOY_HOST, DEPLOY_USER

set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
HOST="${DEPLOY_HOST:?set DEPLOY_HOST}"
USER="${DEPLOY_USER:-atul}"
SSH_PORT="${DEPLOY_SSH_PORT:-22}"
REMOTE_APP=/home/YOUR_APP_USER/cash-center
REMOTE_DJANGO="${REMOTE_APP}/django"

SSH_OPTS=(-o StrictHostKeyChecking=accept-new -p "$SSH_PORT")
if [[ -n "${SSH_KEY_FILE:-}" ]]; then
  SSH_OPTS+=(-i "$SSH_KEY_FILE")
fi
RSYNC_SSH="ssh ${SSH_OPTS[*]}"

echo "==> Sync django/ to ${USER}@${HOST}:${REMOTE_DJANGO}"
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

echo "==> Install deps, migrate, collectstatic, restart gunicorn"
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

echo "==> Deploy complete"

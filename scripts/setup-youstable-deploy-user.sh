#!/usr/bin/env bash
# One-time: create least-privilege CI deploy user on server.
# Run on server as root:
#   sudo bash setup-deploy-user.sh
#
# Or from Mac:
#   scp scripts/setup-deploy-user.sh server:/tmp/
#   ssh YOUR_SSH_TARGET 'sudo bash /tmp/setup-deploy-user.sh'

set -euo pipefail

DEPLOY_USER="${DEPLOY_USER:-cashcenter-deploy}"
APP_DIR="${APP_DIR:-/home/YOUR_APP_USER/cash-center}"
ACTIVATE_SCRIPT=/usr/local/sbin/cashcenter-deploy-activate.sh
GROUP=cashcenter

if [[ "${EUID:-0}" -ne 0 ]]; then
  echo "Run as root (sudo)." >&2
  exit 1
fi

if [[ ! -d "$APP_DIR/django" ]]; then
  echo "Missing ${APP_DIR}/django — adjust APP_DIR." >&2
  exit 1
fi

echo "==> Group and user: ${DEPLOY_USER}"
groupadd -f "$GROUP"
if ! id "$DEPLOY_USER" &>/dev/null; then
  useradd -m -s /bin/bash -g "$GROUP" "$DEPLOY_USER"
fi
chmod 700 "/home/${DEPLOY_USER}"
usermod -aG "$GROUP" atul 2>/dev/null || true

echo "==> Permissions: ${DEPLOY_USER} group-write on app tree (not .env)"
chgrp -R "$GROUP" "$APP_DIR"
chmod -R g+rwX "$APP_DIR"
find "$APP_DIR" -type d -exec chmod g+s {} +
# Keep secrets atul-only
if [[ -f "${APP_DIR}/django/.env" ]]; then
  chown atul:atul "${APP_DIR}/django/.env"
  chmod 600 "${APP_DIR}/django/.env"
fi
# New files from CI rsync stay group-writable
chmod g+s "$APP_DIR" "$APP_DIR/django" 2>/dev/null || true

echo "==> Remote activate script (pip/migrate/collectstatic as atul, restart gunicorn)"
install -m 0755 /dev/stdin "$ACTIVATE_SCRIPT" <<'EOS'
#!/usr/bin/env bash
set -euo pipefail
APP=/home/YOUR_APP_USER/cash-center
cd "$APP"
sudo -u atul "$APP/.venv/bin/pip" install -q -r requirements.txt
cd django
sudo -u atul "$APP/.venv/bin/python" manage.py migrate --noinput
sudo -u atul "$APP/.venv/bin/python" manage.py collectstatic --noinput
systemctl restart gunicorn-cashcenter.service
sleep 2
systemctl is-active --quiet gunicorn-cashcenter.service
echo "gunicorn-cashcenter: active"
EOS

echo "==> sudoers (single allowed command for ${DEPLOY_USER})"
install -m 0440 /dev/stdin /etc/sudoers.d/cashcenter-deploy <<EOF
# Managed by cashcenter scripts/setup-deploy-user.sh
Defaults:${DEPLOY_USER} !requiretty
${DEPLOY_USER} ALL=(root) NOPASSWD: ${ACTIVATE_SCRIPT}
EOF
visudo -cf /etc/sudoers.d/cashcenter-deploy

echo "==> SSH: install public key for ${DEPLOY_USER}"
install -d -m 700 -o "$DEPLOY_USER" -g "$GROUP" "/home/${DEPLOY_USER}/.ssh"
touch "/home/${DEPLOY_USER}/.ssh/authorized_keys"
chown "$DEPLOY_USER:$GROUP" "/home/${DEPLOY_USER}/.ssh/authorized_keys"
chmod 600 "/home/${DEPLOY_USER}/.ssh/authorized_keys"

if [[ -n "${DEPLOY_PUBKEY:-}" ]]; then
  if ! grep -qF "$DEPLOY_PUBKEY" "/home/${DEPLOY_USER}/.ssh/authorized_keys"; then
    echo "$DEPLOY_PUBKEY" >>"/home/${DEPLOY_USER}/.ssh/authorized_keys"
  fi
  echo "Public key installed."
else
  echo "Set DEPLOY_PUBKEY=\"\$(cat key.pub)\" and re-run to add CI public key."
fi

echo "==> Done. Manual atul SSH unchanged."

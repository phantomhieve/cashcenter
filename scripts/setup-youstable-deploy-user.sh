#!/usr/bin/env bash
# One-time: least-privilege CI deploy user on the app server.
# Run as root on the server:
#   sudo APP_OWNER=your-app-user APP_DIR=/home/your-app-user/cash-center \
#        DEPLOY_USER=your-deploy-user DEPLOY_PUBKEY="$(cat deploy.pub)" \
#        bash setup-deploy-user.sh

set -euo pipefail

DEPLOY_USER="${DEPLOY_USER:-cashcenter-deploy}"
APP_OWNER="${APP_OWNER:?set APP_OWNER (UNIX user that owns the app)}"
APP_DIR="${APP_DIR:-/home/${APP_OWNER}/cash-center}"
ACTIVATE_SCRIPT=/usr/local/sbin/cashcenter-deploy-activate.sh
GROUP="${DEPLOY_GROUP:-cashcenter}"

if [[ "${EUID:-0}" -ne 0 ]]; then
  echo "Run as root (sudo)." >&2
  exit 1
fi

if [[ ! -d "$APP_DIR/django" ]]; then
  echo "Missing ${APP_DIR}/django — set APP_DIR." >&2
  exit 1
fi

echo "==> Group and user: ${DEPLOY_USER}"
groupadd -f "$GROUP"
if ! id "$DEPLOY_USER" &>/dev/null; then
  useradd -m -s /bin/bash -g "$GROUP" "$DEPLOY_USER"
fi
chmod 700 "/home/${DEPLOY_USER}"
usermod -aG "$GROUP" "$APP_OWNER" 2>/dev/null || true

echo "==> Permissions: ${DEPLOY_USER} group-write on app tree (not .env)"
chgrp -R "$GROUP" "$APP_DIR"
chmod -R g+rwX "$APP_DIR"
find "$APP_DIR" -type d -exec chmod g+s {} +
if [[ -f "${APP_DIR}/django/.env" ]]; then
  chown "${APP_OWNER}:${APP_OWNER}" "${APP_DIR}/django/.env"
  chmod 600 "${APP_DIR}/django/.env"
fi
chmod g+s "$APP_DIR" "$APP_DIR/django" 2>/dev/null || true

echo "==> Remote activate script"
install -m 0755 /dev/stdin "$ACTIVATE_SCRIPT" <<EOS
#!/usr/bin/env bash
set -euo pipefail
APP="${APP_DIR}"
APP_OWNER="${APP_OWNER}"
cd "\$APP"
sudo -u "\$APP_OWNER" "\$APP/.venv/bin/pip" install -q -r requirements.txt
cd django
sudo -u "\$APP_OWNER" "\$APP/.venv/bin/python" manage.py migrate --noinput
sudo -u "\$APP_OWNER" "\$APP/.venv/bin/python" manage.py collectstatic --noinput
systemctl restart gunicorn-cashcenter.service
sleep 2
systemctl is-active --quiet gunicorn-cashcenter.service
echo "gunicorn-cashcenter: active"
EOS

echo "==> sudoers"
install -m 0440 /dev/stdin /etc/sudoers.d/cashcenter-deploy <<EOF
# Managed by cashcenter setup-deploy-user.sh
Defaults:${DEPLOY_USER} !requiretty
${DEPLOY_USER} ALL=(root) NOPASSWD: ${ACTIVATE_SCRIPT}
EOF
visudo -cf /etc/sudoers.d/cashcenter-deploy

echo "==> SSH authorized_keys for ${DEPLOY_USER}"
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
  echo "Set DEPLOY_PUBKEY and re-run to install CI public key."
fi

echo "==> Done."

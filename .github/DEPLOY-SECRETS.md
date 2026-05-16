# CI/CD secrets (GitHub Actions / GitLab CI)

Store values in your CI provider’s **secret / protected variables** — never commit hosts, users, keys, or paths.

| Secret / variable | Description |
|-------------------|-------------|
| `DEPLOY_SSH_PRIVATE_KEY` | Deploy-only SSH private key (full PEM, including header/footer lines) |
| `DEPLOY_HOST` | Server hostname or IP |
| `DEPLOY_USER` | Dedicated deploy UNIX user (least privilege) |
| `DEPLOY_APP_DIR` | App root on server (e.g. `/home/<app-user>/cash-center`) |
| `DEPLOY_SSH_PORT` | SSH port (optional, default `22`) |
| `DEPLOY_HEALTHCHECK_URL` | Optional URL for post-deploy HTTP check |

## Deploy user model

| Allowed | Blocked |
|---------|---------|
| `rsync` into app directory (group-writable tree) | Read `django/.env` |
| `sudo` **only** the server activate script | Other `sudo`, login as app owner |
| Activate: deps, migrate, collectstatic as app owner; restart app service | Other hosts/paths |

Configure the activate script path and sudoers on the server via `scripts/setup-deploy-user.sh`.

## One-time server setup

```bash
export APP_OWNER=your-app-unix-user
export APP_DIR=/home/${APP_OWNER}/cash-center
export DEPLOY_USER=your-deploy-user
PUB="$(cat /path/to/deploy_key.pub)"
scp scripts/setup-deploy-user.sh YOUR_SSH_TARGET:/tmp/
ssh YOUR_SSH_TARGET "sudo APP_OWNER=$APP_OWNER APP_DIR=$APP_DIR DEPLOY_USER=$DEPLOY_USER DEPLOY_PUBKEY='$PUB' bash /tmp/setup-deploy-user.sh"
```

## fail2ban + GitHub Actions

CI runners use [GitHub Actions IP ranges](https://api.github.com/meta) (`actions` key). On the server:

```bash
sudo EXTRA_IGNORE_IPS="YOUR_HOME_PUBLIC_IP/32" bash scripts/configure-fail2ban-github-actions.sh
```

Adds `/etc/fail2ban/jail.d/sshd-github-actions.local` with those CIDRs in `ignoreip`. Re-run weekly or after GitHub meta changes.

## Local test (before pushing)

```bash
cp .env.deploy.local.example .env.deploy.local   # fill values, never commit
chmod +x scripts/test-deploy-ssh.sh
./scripts/test-deploy-ssh.sh          # SSH + activate only
./scripts/test-deploy-ssh.sh --full   # full rsync deploy
```

## Security audit (on server)

```bash
sudo APP_OWNER=your-app-user APP_DIR=/home/your-app-user/cash-center bash scripts/audit-deploy-security.sh
```

## Manual deploy

```bash
export SSH_KEY_FILE=/path/to/deploy_key
export DEPLOY_HOST=your.server.example
export DEPLOY_USER=your-deploy-user
export DEPLOY_APP_DIR=/home/your-app-user/cash-center
./scripts/deploy-server.sh
```

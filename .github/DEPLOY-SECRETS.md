# CI/CD secrets (GitHub Actions)

Store values in GitHub **Settings → Secrets and variables → Actions** — never commit hosts, users, keys, or paths.

| Secret | Description |
|--------|-------------|
| `DEPLOY_SSH_PRIVATE_KEY` | Deploy-only SSH private key (full PEM, including header/footer lines) |
| `DEPLOY_HOST` | Server hostname or IP |
| `DEPLOY_USER` | Dedicated deploy UNIX user (`cashcenter-deploy`) |
| `DEPLOY_APP_DIR` | App root on server (e.g. `/home/<app-owner>/cash-center`) |
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
export DEPLOY_USER=cashcenter-deploy
PUB="$(cat /path/to/deploy_key.pub)"
scp scripts/setup-deploy-user.sh YOUR_SSH_TARGET:/tmp/
ssh YOUR_SSH_TARGET "sudo APP_OWNER=$APP_OWNER APP_DIR=$APP_DIR DEPLOY_USER=$DEPLOY_USER DEPLOY_PUBKEY='$PUB' bash /tmp/setup-deploy-user.sh"
```

Also ensure `sshd` allows the deploy user (`AllowUsers atul cashcenter-deploy root`) and `/home/<app-owner>` is traversable (`chmod 751`).

## fail2ban + GitHub Actions

CI runners use [GitHub Actions IP ranges](https://api.github.com/meta). On the server:

```bash
sudo EXTRA_IGNORE_IPS="YOUR_HOME_PUBLIC_IP" bash scripts/configure-fail2ban-github-actions.sh
```

Adds `/etc/fail2ban/jail.d/sshd-github-actions.local` with those CIDRs in `ignoreip`.

## Local test (before pushing)

```bash
export SSH_KEY_FILE=/path/to/deploy_key
export DEPLOY_HOST=your.server.example
export DEPLOY_USER=cashcenter-deploy
export DEPLOY_APP_DIR=/home/your-app-owner/cash-center
export DEPLOY_HEALTHCHECK_URL=https://your-public-site.example/
./scripts/deploy-server.sh
```

## Manual deploy

Same as local test above, or trigger **Actions → Deploy Server → Run workflow** after secrets are set.

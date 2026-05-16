# CI/CD secrets (GitHub Actions / GitLab CI)

Dedicated deploy user on server: **`cashcenter-deploy`** (not `atul`).

| Secret | Value |
|--------|--------|
| `DEPLOY_SSH_PRIVATE_KEY` | Contents of `~/.ssh/deploy_key` (private key) |
| `DEPLOY_HOST` | `YOUR_DEPLOY_HOST` |
| `DEPLOY_USER` | `cashcenter-deploy` |
| `DEPLOY_SSH_PORT` | `22` (optional) |

```bash
cat ~/.ssh/deploy_key
```

## What the deploy user can do

| Allowed | Blocked |
|---------|---------|
| `rsync` into `/home/YOUR_APP_USER/cash-center/` (group `cashcenter`) | Read `django/.env` (mode 600, owner `atul`) |
| `sudo /usr/local/sbin/cashcenter-deploy-activate.sh` only | Any other `sudo`, shell as `atul` |
| Activate runs pip/migrate/collectstatic **as atul**, restarts gunicorn | SSH to other hosts, other paths |

Manual admin SSH as **`atul`** is unchanged.

## One-time server setup

Already applied via `scripts/setup-deploy-user.sh`. To re-run (e.g. rotate key):

```bash
PUB=$(cat ~/.ssh/deploy_key.pub)
scp scripts/setup-deploy-user.sh server:/tmp/
ssh YOUR_SSH_TARGET "sudo DEPLOY_PUBKEY='$PUB' bash /tmp/setup-deploy-user.sh"
```

## Local test

```bash
SSH_KEY_FILE=~/.ssh/deploy_key \
DEPLOY_HOST=YOUR_DEPLOY_HOST \
DEPLOY_USER=cashcenter-deploy \
./scripts/deploy-server.sh
```

## GitLab CI

Use the same env vars in protected CI variables and run `./scripts/deploy-server.sh` in a deploy job (see `.gitlab-ci.yml` if present).

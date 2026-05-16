# GitHub Actions deploy secrets

Add these in **Settings → Secrets and variables → Actions** for `phantomhieve/cashcenter`:

| Secret | Example | Required |
|--------|---------|----------|
| `DEPLOY_SSH_PRIVATE_KEY` | Full private key (ed25519), including `BEGIN`/`END` lines | Yes |
| `DEPLOY_HOST` | `YOUR_DEPLOY_HOST` | Yes |
| `DEPLOY_USER` | `atul` | Yes |
| `DEPLOY_SSH_PORT` | `22` | No (defaults to 22) |

## One-time server setup

On your Mac, create a deploy-only key and install the public key on server:

```bash
ssh-keygen -t ed25519 -f ~/.ssh/deploy_key -N "" -C "github-actions-cashcenter"
ssh-copy-id -i ~/.ssh/deploy_key.pub atul@YOUR_DEPLOY_HOST
```

Copy the private key into GitHub:

```bash
cat ~/.ssh/deploy_key
```

Paste into secret `DEPLOY_SSH_PRIVATE_KEY`.

## Triggers

- Push or merge to `master` or `main`
- Manual: **Actions → Deploy Server → Run workflow**

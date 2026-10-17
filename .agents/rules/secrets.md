# Secret & Credentials Policy

## Policy:
1. **Never Look at Secrets**:
   - **NEVER** view, open, inspect, or output `.env`, `.env.*` (except `.env.example` / `.env_example`), `*.key.json`, service account credentials, passwords, or secret tokens.
   - Never output credentials or secret tokens to stdout, terminal logs, or git commits.

2. **Defense in Depth**:
   - Always verify that `.gitignore` ignores `.env`, `.env.deploy.local`, private keys, and temporary credentials.
   - Use mock credentials or explicit environment variable references in documentation and test suites.

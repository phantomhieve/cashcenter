# CashCenter — Agent Guidelines & Repository Contract

## Core Mission & Architecture
CashCenter provides a secure, streamlined data management system for wholesale textile and shop operations:
- **Ledger Management (`ledger`, `ledger_base`)**: Transport bills, L/R numbers, incoming supplier receipts, freight calculations, and delivery tracking.
- **Order Management (`orderlist`)**: Customer orders, fulfillment tracking with parcel reconciliation, order modes (Phone, WhatsApp, Physical, Agent), and status lifecycle.
- **Rate List Management (`ratelist`)**: Product pricing, purchase price vs sell price history, and company item tracking.
- **Stock Management (`stock`)**: Fabric stock inventory categorized by HSN, rate, and meters/pieces.
- **Security & Financial Years (`core`)**: Multi-year financial partition, user session controls, and admin password protection (`_verify_fy_password`).
- **AI Market Intelligence (`intelligence`)**: Multi-stage Directed Acyclic Graph (DAG) workflow engine driving insights from noisy sold data, web product discovery, automated comprehensive prompt generation with Argon, and reflective feedback loops.

---

## Agent Ground Rules

### 1. Never Look at Secrets
- **NEVER** view, open, inspect, or output `.env`, `.env.*` (except `.env_example`), `*.key.json`, service account credentials, passwords, or tokens.
- Never output credentials or secret tokens to terminal stdout, logs, or commit diffs.

### 2. Update and Use CodeGraph
- **Explore First**: Call `codegraph_explore` MCP tool or `/opt/homebrew/bin/codegraph explore <query>` CLI before making edits to inspect source symbols, call chains, and blast radius.
- **Keep Synchronized**: Run `codegraph sync` after code changes or file additions.
- Do not commit `.codegraph/codegraph.db` (enforced by `.codegraph/.gitignore`).

### 3. Pre-Commit Hooks
- Pre-commit checks are located in `scripts/pre-commit.sh` and linked to `.git/hooks/pre-commit`.
- The hook verifies:
  1. No secrets, keys, or credential files are staged.
  2. CodeGraph index is synced (`codegraph sync`).
  3. Django system check passes (`python manage.py check`).
  4. No merge conflict markers are staged.

### 4. Proper Commit Messages
- Use clear, concise, imperative messages following the repository convention:
  - Format: `<type>: <summary>` (e.g., `feat: ...`, `fix: ...`, `refactor: ...`).
  - First line: Capitalized imperative summary (<72 chars).
  - Body: Explain the motivation, rationale, and impact of the change.

### 5. Layout & UI Integrity
- **CRITICAL**: Do NOT change the layout or CSS of the existing apps (`ledger`, `orderlist`, `ratelist`, `stock`, `user`).
- New apps (such as `intelligence`) provide self-contained, modern, premium interfaces without polluting legacy style definitions.

### 6. Admin Password Security
- Sensitive operational views (such as Financial Year switching and AI Market Intelligence) MUST be protected by the user's admin password (`_verify_fy_password`).

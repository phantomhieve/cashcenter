# CodeGraph Usage & Synchronization

## Policy:
1. **Explore First**:
   - Before answering architectural questions or modifying symbols, query the knowledge graph via the `codegraph_explore` MCP tool or `codegraph explore <query>` CLI.
   - Inspect the returned blast radius (callers and callees) to ensure dependent components and models are accounted for.

2. **Keep Synchronized**:
   - After adding, renaming, or refactoring symbols or files, ensure the knowledge graph is synchronized by running `codegraph sync`.
   - Never commit the SQLite database `.codegraph/codegraph.db` (enforced by `.codegraph/.gitignore`).

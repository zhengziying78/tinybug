# Temporal

Temporal workflows, activities, and GitHub integrations that power the mutation
testing MVP.

## Package Layout

- `temporal/workflows/`: Temporal workflow definitions, activity helpers, storage,
  and orchestration utilities suitable for production use beyond the original
  demo scripts.
- `temporal/github/`: GitHub-facing helpers (check processing, repo and PR
  management, test analysis) shared by activities and future services.

The legacy modules under `scripts/demo/workflow/` and `scripts/demo/github/` have
been retained only as thin wrappers for backward compatibility with the demo CLI.
New code should import directly from the `temporal.*` packages.

## Tech Stack

- Temporal Python SDK
- Temporal Cloud for orchestration
- Multi-tenant namespace isolation

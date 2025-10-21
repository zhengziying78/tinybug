# Temporal

Temporal workflows, activities, and GitHub integrations that power the mutation
testing MVP.

## Package Layout

- `temporal/workflows/`: Temporal workflow definitions, activity helpers, storage,
  and orchestration utilities suitable for production use beyond the original
  demo scripts.
- `temporal/github/`: GitHub-facing helpers (check processing, repo and PR
  management, test analysis) shared by activities and future services.
- `temporal/mutation/`: Repository-specific mutation presets consumed by
  Temporal workflows.

Legacy demo-only helpers now live exclusively under `scripts/demo/workflow/flow.py`
for the console experience; all reusable code resides in the `temporal.*` packages.

## Tech Stack

- Temporal Python SDK
- Temporal Cloud for orchestration
- Multi-tenant namespace isolation

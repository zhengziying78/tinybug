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

Legacy demo-only helpers now live inside `scripts/demo/demo.py` for the console
experience; all reusable code resides in the `temporal.*` packages.

## Tech Stack

- Temporal Python SDK
- Temporal Cloud for orchestration
- Multi-tenant namespace isolation

## Running the Worker & Workflow

- `temporal/workflows/temporal_worker.py` registers activities and the
  `RunSingleMutationWorkflow` that mirrors the demo steps. Run it as a worker:

  ```bash
  python -m temporal.workflows.temporal_worker --task-queue mutation-demo-task-queue
  ```

- `temporal/workflows/start_temporal_workflow.py` connects to Temporal and starts the
  workflow:

  ```bash
  python -m temporal.workflows.start_temporal_workflow --repo demo-httpie-cli --wait
  ```

- Use the Temporal CLI to observe workflow execution (requires the `temporal` CLI):

  ```bash
  temporal workflow trace -w mutation-demo-20251018-184437
  ```

- Mutation summaries are written to the `mutation_results/` directory by default.
  Override the location with `--summary-dir` when launching the workflow or rely on
  the default directory.

Set `--address` and `--namespace` to match your Temporal environment. The `--wait`
flag waits for completion and prints the structured result.

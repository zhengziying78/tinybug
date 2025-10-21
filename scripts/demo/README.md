# Demo Scripts

This directory contains scripts for running mutation testing demos and managing GitHub pull requests.

## Files

- `demo.py` - Main mutation testing demo script
- `workflow/flow.py` - Demo runner that consumes the production-ready helpers under `temporal/workflows/`
- `cleanup_github.py` - Utility to clean up open pull requests in demo repositories

## demo.py

Runs a complete mutation testing proof-of-concept demo that:
1. Clones a demo repository
2. Creates a branch and applies a mutation
3. Creates a pull request
4. Waits for CI checks to complete
5. Analyzes the results
6. Cleans up the repository and PR

### Usage

```bash
python -m scripts.demo.demo [repo_name]
```

**Arguments:**
- `repo_name` (optional) - Repository to test. Options:
  - `demo-httpie-cli` - HTTPie CLI mutation test
  - `demo-pallets-click` - Pallets Click mutation test  
  - `demo-psf-requests` - PSF Requests mutation test

If no repository is specified, an interactive menu will appear with a 10-second timeout that defaults to `demo-httpie-cli`.

### Examples

```bash
# Run with interactive repository selection
python -m scripts.demo.demo

# Run with specific repository
python -m scripts.demo.demo demo-httpie-cli
python -m scripts.demo.demo demo-pallets-click
python -m scripts.demo.demo demo-psf-requests
```

### What it does

The script performs these steps:
1. **Repository Selection** - Choose from 3 predefined demo repositories
2. **Clone Repository** - Downloads the selected repository
3. **Create Branch** - Creates a timestamped branch for the mutation
4. **Apply Mutation** - Makes a specific code change to test the test suite
5. **Create Pull Request** - Opens a PR with the mutation
6. **Wait for CI** - Monitors CI checks (10 minute timeout)
7. **Analyze Results** - Determines if the mutation was "killed" by tests
8. **Cleanup** - Removes the repository and closes the PR

Results are saved to a timestamped JSON file in the `mutation_results/` directory (created in your current working directory).

## Temporal Worker & Workflow

The demo flow can also be executed via Temporal:

- `temporal/workflows/temporal_worker.py` registers activities and the `RunSingleMutationWorkflow` that mirrors the demo steps. Run it as a worker:

  ```bash
  python -m temporal.workflows.temporal_worker --task-queue mutation-demo-task-queue
  ```

- `temporal/workflows/start_temporal_workflow.py` connects to Temporal and starts the workflow:

  ```bash
  python -m temporal.workflows.start_temporal_workflow --repo demo-httpie-cli --wait
  ```

- Use the Temporal CLI to observe workflow execution (requires `temporal` CLI):

  ```bash
  temporal workflow trace -w mutation-demo-20251018-184437
  ```

- Mutation summaries are written to the `mutation_results/` directory by default. Override the location with `--summary-dir` when launching the workflow or rely on the default directory.

Set `--address` and `--namespace` to match your Temporal environment. The `--wait` flag waits for completion and prints the structured result.

## cleanup_github.py

Utility script to close all open pull requests in the three demo repositories. Useful for cleaning up after running multiple demo sessions.

### Usage

```bash
python cleanup_github.py
```

**Prerequisites:**
- GitHub CLI (`gh`) must be installed and authenticated
- Access to the demo repositories

### What it does

1. **Check Repositories** - Scans all three demo repositories for open PRs
2. **Close PRs** - Closes each open pull request found
3. **Summary** - Reports how many PRs were closed and any failures

The script targets these repositories:
- `https://github.com/zhengziying78/demo-httpie-cli`
- `https://github.com/zhengziying78/demo-pallets-click`
- `https://github.com/zhengziying78/demo-psf-requests`

## Dependencies

Scripts require:
- Python 3.9+
- GitHub CLI (`gh`) installed and authenticated
- Internet connection and access to the demo repositories
- Temporal Python SDK (`temporalio`) when using the worker/workflow scripts (install with `pip install temporalio` or add it to your project dependencies)

## Repository Structure

The demo uses three forked repositories, each with a specific mutation:

1. **demo-httpie-cli** - Tests None check logic in `httpie/cli/dicts.py`
2. **demo-pallets-click** - Tests encoding assignment in `src/click/utils.py`
3. **demo-psf-requests** - Tests status code description in `src/requests/status_codes.py`

Each mutation is designed to test whether the repository's test suite can detect the intentional code change.

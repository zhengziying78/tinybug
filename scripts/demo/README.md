# Demo Scripts

This directory contains scripts for running mutation testing demos and managing GitHub pull requests.

## Files

- `demo.py` - Main mutation testing demo script
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
python demo.py [repo_name]
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
python demo.py

# Run with specific repository
python demo.py demo-httpie-cli
python demo.py demo-pallets-click
python demo.py demo-psf-requests
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

Results are saved to a timestamped JSON file in the current directory.

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

Both scripts require:
- Python 3.7+
- GitHub CLI (`gh`) installed and authenticated
- Internet connection
- Access to the demo repositories

## Repository Structure

The demo uses three forked repositories, each with a specific mutation:

1. **demo-httpie-cli** - Tests None check logic in `httpie/cli/dicts.py`
2. **demo-pallets-click** - Tests encoding assignment in `src/click/utils.py`
3. **demo-psf-requests** - Tests status code description in `src/requests/status_codes.py`

Each mutation is designed to test whether the repository's test suite can detect the intentional code change.
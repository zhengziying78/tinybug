# Sample Data for Testing

This directory contains real data captured from GitHub API calls during demo runs. The data serves two purposes:

1. **Human Reference** - To see the exact data structure and values we receive from GitHub API
2. **Unit Test Data** - To serve as test fixtures for unit test cases

## Data Types

### PR Status Data
- `pr_status_<repo>_<timestamp>.json` - Pull request status from `gh pr view` command
- Contains: PR number, title, state, mergeable status, statusCheckRollup, URL

### Check Data  
- `checks_<repo>_<timestamp>.json` - Check results from `gh pr checks` command
- Contains: Individual check details with name, state, bucket, timing, workflow info

### Combined Results
- `pr_results_<repo>_<timestamp>.json` - Combined data structure passed to test analyzer
- Contains: Both status and checks data plus completion flags

## Data Capture

Data is automatically captured when running demo.py with the `--capture-data` flag:

```bash
python scripts/demo/demo.py demo-httpie-cli --capture-data
python scripts/demo/demo.py demo-pallets-click --capture-data  
python scripts/demo/demo.py demo-psf-requests --capture-data
```

## File Naming Convention

Files are named with the pattern: `<data_type>_<repo>_<timestamp>.json`

- `<data_type>`: pr_status, checks, or pr_results
- `<repo>`: httpie-cli, pallets-click, or psf-requests
- `<timestamp>`: YYYYMMDD_HHMMSS format

## Usage in Tests

These files can be loaded as test fixtures:

```python
import json
from pathlib import Path

def load_sample_data(filename):
    sample_data_dir = Path(__file__).parent / "sample_data"
    with open(sample_data_dir / filename) as f:
        return json.load(f)

# Example usage
pr_status = load_sample_data("pr_status_httpie-cli_20250711_123456.json")
checks = load_sample_data("checks_httpie-cli_20250711_123456.json")
```
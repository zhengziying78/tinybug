"""
Persistence helpers for storing mutation workflow results.
"""
from __future__ import annotations

import json
import re
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional, Union

DEFAULT_RESULTS_DIR_NAME = "mutation_results"


def _sanitize_filename(value: str) -> str:
    """Return a filesystem-safe representation of the value."""
    safe = re.sub(r"[^A-Za-z0-9_.-]+", "-", value.strip())
    return safe.strip("-") or "result"


def _default_results_dir() -> Path:
    """Compute the default directory for storing mutation results."""
    return Path.cwd() / DEFAULT_RESULTS_DIR_NAME


def persist_flow_result(
    result_data: Dict[str, Any],
    base_dir: Optional[Union[str, Path]] = None,
) -> Path:
    """
    Persist the mutation workflow result to disk and return the file path.

    Args:
        result_data: Dictionary representation of MutationFlowResult.
        base_dir: Optional override of the directory to store results.

    Returns:
        Path to the stored JSON file.
    """
    metadata = result_data.get("metadata", {}) or {}
    timestamp = metadata.get("timestamp") or datetime.now().strftime("%Y%m%d-%H%M%S")
    repo_identifier = (
        metadata.get("repo_id")
        or result_data.get("branch_name")
        or result_data.get("repo_url", "repo")
    )

    repo_slug = _sanitize_filename(str(repo_identifier).split("/")[-1])
    filename = f"{timestamp}_{repo_slug}_mutation_result.json"

    target_dir = Path(base_dir) if base_dir else _default_results_dir()
    target_dir.mkdir(parents=True, exist_ok=True)

    output_path = target_dir / filename
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result_data, handle, indent=2, ensure_ascii=False)

    return output_path

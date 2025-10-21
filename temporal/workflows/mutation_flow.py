"""
Reusable mutation workflow structures shared across Temporal orchestrations.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, Mapping, Optional


def build_pr_body(mutation_config: Mapping[str, Any]) -> str:
    """Construct the pull request body for a mutation."""
    return f"""
This PR contains a mutation for testing purposes.

**Mutation Details:**
- File: {mutation_config['file_path']}
- Line: {mutation_config['line_number']}
- Change: `{mutation_config['find_pattern']}` → `{mutation_config['replace_pattern']}`

This mutation tests whether the test suite can detect the change in {mutation_config['description'].lower()}.
"""


def generate_mutation_metadata(
    mutation_config: Mapping[str, Any],
    *,
    timestamp: Optional[str] = None,
) -> Dict[str, str]:
    """Generate branch name and PR details for a mutation run."""
    run_timestamp = timestamp or datetime.now().strftime("%Y%m%d-%H%M%S")
    branch_name = f"mutation-test-demo-{run_timestamp}"
    pr_title = f"Mutation Test: {mutation_config['description']} ({run_timestamp})"
    pr_body = build_pr_body(mutation_config)
    return {
        "timestamp": run_timestamp,
        "branch_name": branch_name,
        "pr_title": pr_title,
        "pr_body": pr_body,
    }


@dataclass
class MutationFlowResult:
    """Structured result emitted by the single-mutation workflow."""

    repo_url: str
    branch_name: str
    pr_title: str
    mutation_description: str
    pr_number: Optional[str] = None
    pr_url: Optional[str] = None
    mutation_applied: bool = False
    analysis: Optional[Dict[str, Any]] = None
    results_file: Optional[str] = None
    pr_results: Optional[Dict[str, Any]] = None
    cleanup_details: Optional[Dict[str, Any]] = None
    summary_file: Optional[str] = None
    error: Optional[str] = None
    traceback: Optional[str] = None
    repo_path: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Return a JSON-serializable representation of the run."""
        return {
            "repo_url": self.repo_url,
            "branch_name": self.branch_name,
            "pr_title": self.pr_title,
            "mutation_description": self.mutation_description,
            "pr_number": self.pr_number,
            "pr_url": self.pr_url,
            "mutation_applied": self.mutation_applied,
            "analysis": self.analysis,
            "results_file": self.results_file,
            "summary_file": self.summary_file,
            "pr_results": self.pr_results,
            "cleanup_details": self.cleanup_details,
            "error": self.error,
            "traceback": self.traceback,
            "repo_path": self.repo_path,
            "metadata": self.metadata,
        }


__all__ = [
    "build_pr_body",
    "generate_mutation_metadata",
    "MutationFlowResult",
]

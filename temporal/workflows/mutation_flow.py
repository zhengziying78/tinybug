"""
Reusable mutation workflow structures shared across Temporal orchestrations.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime
from typing import Any, Dict, Mapping, Optional

from models.mutation.context import MutationContext
from models.mutation.result import MutationResult


def build_pr_body(mutation_config: Mapping[str, Any]) -> str:
    """Construct the pull request body for a mutation."""
    description = mutation_config['description'].lower()
    return (
        "\n"
        "This PR contains a mutation for testing purposes.\n\n"
        "**Mutation Details:**\n"
        f"- File: {mutation_config['file_path']}\n"
        f"- Line: {mutation_config['line_number']}\n"
        f"- Change: `{mutation_config['find_pattern']}` → "
        f"`{mutation_config['replace_pattern']}`\n\n"
        "This mutation tests whether the test suite can detect the change in "
        f"{description}.\n"
    )


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
class WorkflowMutationRun:
    """Workflow-scoped metadata captured alongside the mutation results."""

    repo_path: Optional[str] = None
    cleanup_details: Optional[Dict[str, Any]] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class MutationFlowResult:
    """Structured result emitted by the single-mutation workflow."""

    context: MutationContext
    outcome: MutationResult
    workflow: WorkflowMutationRun = field(default_factory=WorkflowMutationRun)

    def to_dict(self) -> Dict[str, Any]:
        """Return a JSON-serializable representation of the run."""
        return {
            "context": asdict(self.context),
            "outcome": asdict(self.outcome),
            "workflow": asdict(self.workflow),
        }


__all__ = [
    "MutationContext",
    "MutationResult",
    "WorkflowMutationRun",
    "MutationFlowResult",
    "build_pr_body",
    "generate_mutation_metadata",
]

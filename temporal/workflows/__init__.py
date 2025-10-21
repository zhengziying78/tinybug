"""
Temporal workflow building blocks for the mutation-testing MVP.

This package exposes commonly-used helpers via lazy attribute access so the
modules can still be executed directly (e.g. ``python -m temporal.workflows.temporal_worker``)
without triggering premature imports.
"""
from __future__ import annotations

import importlib
from typing import Any, Dict, Tuple

_EXPORTS: Dict[str, Tuple[str, str]] = {
    # Activity helpers
    "analyze_test_results": (
        "temporal.workflows.activities",
        "analyze_test_results",
    ),
    "apply_mutation": (
        "temporal.workflows.activities",
        "apply_mutation",
    ),
    "cleanup_pull_request_and_repo": (
        "temporal.workflows.activities",
        "cleanup_pull_request_and_repo",
    ),
    "clone_repository": (
        "temporal.workflows.activities",
        "clone_repository",
    ),
    "commit_and_push_changes": (
        "temporal.workflows.activities",
        "commit_and_push_changes",
    ),
    "create_branch": (
        "temporal.workflows.activities",
        "create_branch",
    ),
    "create_pull_request": (
        "temporal.workflows.activities",
        "create_pull_request",
    ),
    "wait_for_checks": (
        "temporal.workflows.activities",
        "wait_for_checks",
    ),
    # Cleanup utilities
    "CleanupManager": ("temporal.workflows.cleanup", "CleanupManager"),
    # Mutation workflow data structures
    "MutationFlowResult": (
        "temporal.workflows.mutation_flow",
        "MutationFlowResult",
    ),
    "build_pr_body": (
        "temporal.workflows.mutation_flow",
        "build_pr_body",
    ),
    "generate_mutation_metadata": (
        "temporal.workflows.mutation_flow",
        "generate_mutation_metadata",
    ),
    # Persistence & summary helpers
    "persist_flow_result": ("temporal.workflows.storage", "persist_flow_result"),
    "render_summary_lines": ("temporal.workflows.summary", "render_summary_lines"),
    # Temporal worker utilities
    "MutationWorkflowParams": (
        "temporal.workflows.temporal_worker",
        "MutationWorkflowParams",
    ),
    "PersistResultInput": (
        "temporal.workflows.temporal_worker",
        "PersistResultInput",
    ),
    "RunSingleMutationWorkflow": (
        "temporal.workflows.temporal_worker",
        "RunSingleMutationWorkflow",
    ),
    "run_worker": ("temporal.workflows.temporal_worker", "run_worker"),
}

__all__ = list(_EXPORTS.keys())


def __getattr__(name: str) -> Any:
    try:
        module_name, attr_name = _EXPORTS[name]
    except KeyError as exc:  # pragma: no cover - defensive
        raise AttributeError(f"module {__name__!r} has no attribute {name!r}") from exc
    module = importlib.import_module(module_name)
    return getattr(module, attr_name)


def __dir__() -> list[str]:  # pragma: no cover - cosmetic
    return sorted(__all__)

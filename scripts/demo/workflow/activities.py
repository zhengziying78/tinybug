"""
Reusable helper functions that mirror the core steps of the demo workflow.

Each function performs a single side-effecting action and defers to the
existing repository, pull-request, mutation, and analysis utilities. Keeping
them small and idempotent makes them suitable for reuse as Temporal activities.
"""
from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, Mapping, Optional, Tuple

from cleanup import CleanupManager
from github.pr_manager import PRManager
from github.repo_manager import RepoManager
from github.test_analyzer import TestAnalyzer
from mutation.mutator import Mutator, MutationSpec


def clone_repository(repo_url: str, base_dir: Optional[str] = None) -> Path:
    """Clone the target repository and return the local path."""
    repo_manager = RepoManager(base_dir=base_dir or "~/Repos")
    return repo_manager.clone_repo(repo_url)


def create_branch(repo_path: Path, branch_name: str) -> None:
    """Create (or reset) the working branch in the cloned repository."""
    repo_manager = RepoManager()
    repo_manager.create_branch(repo_path, branch_name)


def apply_mutation(repo_path: Path, mutation_config: Mapping[str, Any]) -> bool:
    """Apply the configured mutation to the repository checkout."""
    mutator = Mutator(repo_path)
    mutation_spec = MutationSpec(
        file_path=mutation_config["file_path"],
        line_number=mutation_config["line_number"],
        find_pattern=mutation_config["find_pattern"],
        replace_pattern=mutation_config["replace_pattern"],
    )
    return mutator.apply_mutation(mutation_spec)


def commit_and_push_changes(repo_path: Path, branch_name: str, commit_message: str) -> None:
    """Commit local changes (if any) and push the branch to origin."""
    repo_manager = RepoManager()
    repo_manager.commit_changes(repo_path, commit_message)
    repo_manager.push_branch(repo_path, branch_name)


def create_pull_request(
    repo_path: Path,
    title: str,
    body: str,
    *,
    base_branch: str = "main",
    repo_id: Optional[str] = None,
) -> Dict[str, str]:
    """Open a pull request for the pushed branch and return metadata."""
    pr_manager = PRManager(repo_path)
    return pr_manager.create_pull_request(title, body, base_branch=base_branch, repo=repo_id)


def wait_for_checks(
    repo_path: Path,
    pr_number: str,
    *,
    timeout_seconds: int = 600,
    repo_id: Optional[str] = None,
) -> Dict[str, Any]:
    """Poll GitHub checks for the pull request until completion or timeout."""
    pr_manager = PRManager(repo_path)
    return pr_manager.wait_for_checks(pr_number, timeout_seconds=timeout_seconds, repo=repo_id)


def analyze_test_results(
    repo_path: Path,
    pr_results: Dict[str, object],
    *,
    repo_id: Optional[str] = None,
    output_dir: Optional[Path] = None,
) -> Tuple[Dict[str, Any], Path]:
    """Analyze PR check results and persist the structured summary."""
    analyzer = TestAnalyzer(output_dir=output_dir, repo_path=repo_path)
    analysis = analyzer.analyze_pr_results(pr_results, repo=repo_id)
    results_file = analyzer.save_results(analysis)
    return analysis, results_file


def cleanup_pull_request_and_repo(
    repo_path: Optional[Path],
    *,
    pr_number: Optional[str] = None,
    repo_id: Optional[str] = None,
) -> Dict[str, Any]:
    """Close any open pull request and delete the local checkout."""
    if repo_path is None:
        return {"pr_closed": False, "repo_deleted": False, "errors": ["Missing repo_path"]}

    if pr_number:
        cleanup_manager = CleanupManager()
        return cleanup_manager.cleanup_pr_and_repo(repo_path, pr_number, repo_id)

    repo_manager = RepoManager()
    repo_manager.cleanup_repo(repo_path)
    return {"pr_closed": False, "repo_deleted": True, "errors": []}

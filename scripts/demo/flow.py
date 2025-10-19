"""
Orchestration helpers for running the single-mutation demo workflow.

The coordinator function stitches together the lower-level activity helpers so
we can reuse the same sequence from the CLI and, later, from Temporal workflows.
"""
from __future__ import annotations

import traceback
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, Mapping, Optional

from activities import (
    analyze_test_results,
    apply_mutation,
    cleanup_pull_request_and_repo,
    clone_repository,
    commit_and_push_changes,
    create_branch,
    create_pull_request,
    wait_for_checks,
)


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
            "pr_results": self.pr_results,
            "cleanup_details": self.cleanup_details,
            "error": self.error,
            "traceback": self.traceback,
            "repo_path": self.repo_path,
            "metadata": self.metadata,
        }


def run_single_mutation_flow(
    repo_config: Mapping[str, Any],
    *,
    branch_name: str,
    pr_title: str,
    pr_body: str,
    timeout_seconds: int = 600,
    output_dir: Optional[Path] = None,
    base_clone_dir: Optional[str] = None,
) -> MutationFlowResult:
    """
    Execute the single-mutation demo workflow and return structured results.

    Args:
        repo_config: Repository configuration dict containing keys:
            - url: repository git URL
            - base_branch: base branch name
            - repo_id: GitHub owner/repo identifier
            - mutation: mutation configuration dict
        branch_name: Name of the branch used for the mutation.
        pr_title: Title for the demo pull request.
        pr_body: Body content for the demo pull request.
        timeout_seconds: Max time to wait for GitHub checks (default 10 minutes).
        output_dir: Optional directory for persisting analysis results.
        base_clone_dir: Optional base directory for cloning repositories.

    Returns:
        MutationFlowResult encapsulating the outcome of the run.
    """
    mutation_config = repo_config["mutation"]
    base_branch = repo_config["base_branch"]
    repo_url = repo_config["url"]
    repo_id = repo_config.get("repo_id")

    result = MutationFlowResult(
        repo_url=repo_url,
        branch_name=branch_name,
        pr_title=pr_title,
        mutation_description=mutation_config["description"],
        metadata={
            "repo_id": repo_id,
            "base_branch": base_branch,
        },
    )

    repo_path: Optional[Path] = None
    pr_number: Optional[str] = None

    def log(message: str) -> None:
        print(f"[flow] {message}")

    try:
        log(f"Cloning repository {repo_url}")
        repo_path = clone_repository(repo_url, base_dir=base_clone_dir)
        result.repo_path = str(repo_path)

        log(f"Creating branch {branch_name}")
        create_branch(repo_path, branch_name)

        log("Applying mutation")
        mutation_applied = apply_mutation(repo_path, mutation_config)
        result.mutation_applied = mutation_applied
        if mutation_applied:
            log("Mutation applied successfully")
        else:
            log("No changes made during mutation")

        log("Committing and pushing mutation")
        commit_and_push_changes(repo_path, branch_name, f"Apply mutation: {mutation_config['description']}")

        log("Creating pull request")
        pr_info = create_pull_request(
            repo_path,
            pr_title,
            pr_body,
            base_branch=base_branch,
            repo_id=repo_id,
        )
        pr_number = pr_info["number"]
        result.pr_number = pr_number
        result.pr_url = pr_info.get("url")
        log(f"Pull request created: {result.pr_url}")

        log("Waiting for GitHub checks to complete")
        pr_results = wait_for_checks(
            repo_path,
            pr_number,
            timeout_seconds=timeout_seconds,
            repo_id=repo_id,
        )
        result.pr_results = pr_results
        log("Checks completed")

        log("Analyzing test results")
        analysis, results_file = analyze_test_results(
            repo_path,
            pr_results,
            repo_id=repo_id,
            output_dir=output_dir,
        )
        result.analysis = analysis
        result.results_file = str(results_file)
        log(f"Analysis saved to {result.results_file}")
    except Exception as exc:
        result.error = str(exc)
        result.traceback = traceback.format_exc()
        log(f"Encountered error: {exc}")
    finally:
        log("Cleaning up repository and pull request")
        cleanup_details = cleanup_pull_request_and_repo(
            repo_path,
            pr_number=pr_number,
            repo_id=repo_id,
        )
        result.cleanup_details = cleanup_details

    return result

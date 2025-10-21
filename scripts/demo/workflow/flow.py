"""
Legacy orchestration helpers for the single-mutation demo workflow.

The demo entry points continue to import ``run_single_mutation_flow`` from this
module, while the reusable building blocks now live under ``temporal.workflows``.
"""
from __future__ import annotations

import traceback
from pathlib import Path
from typing import Any, Dict, Mapping, Optional

from temporal.workflows.activities import (
    analyze_test_results,
    apply_mutation,
    cleanup_pull_request_and_repo,
    clone_repository,
    commit_and_push_changes,
    create_branch,
    create_pull_request,
    wait_for_checks,
)
from temporal.workflows.mutation_flow import (
    MutationFlowResult,
    generate_mutation_metadata,
)
from temporal.workflows.storage import persist_flow_result


def run_single_mutation_flow(
    repo_config: Mapping[str, Any],
    *,
    timeout_seconds: int = 600,
    output_dir: Optional[Path] = None,
    base_clone_dir: Optional[str] = None,
    summary_output_dir: Optional[Path] = None,
    timestamp: Optional[str] = None,
) -> MutationFlowResult:
    """
    Execute the single-mutation demo workflow and return structured results.

    Args:
        repo_config: Repository configuration dict containing keys:
            - url: repository git URL
            - base_branch: base branch name
            - repo_id: GitHub owner/repo identifier
            - mutation: mutation configuration dict
        timeout_seconds: Max time to wait for GitHub checks (default 10 minutes).
        output_dir: Optional directory for persisting analysis results.
        base_clone_dir: Optional base directory for cloning repositories.
        timestamp: Optional timestamp override used for naming artifacts.

    Returns:
        MutationFlowResult encapsulating the outcome of the run.
    """
    mutation_config = repo_config["mutation"]
    base_branch = repo_config["base_branch"]
    repo_url = repo_config["url"]
    repo_id = repo_config.get("repo_id")

    mutation_metadata = generate_mutation_metadata(mutation_config, timestamp=timestamp)
    branch_name = mutation_metadata["branch_name"]
    pr_title = mutation_metadata["pr_title"]
    pr_body = mutation_metadata["pr_body"]

    result = MutationFlowResult(
        repo_url=repo_url,
        branch_name=branch_name,
        pr_title=pr_title,
        mutation_description=mutation_config["description"],
        metadata={
            "repo_id": repo_id,
            "base_branch": base_branch,
            "timestamp": mutation_metadata["timestamp"],
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
        commit_and_push_changes(
            repo_path, branch_name, f"Apply mutation: {mutation_config['description']}"
        )

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

        try:
            summary_path = persist_flow_result(
                result.to_dict(),
                summary_output_dir,
            )
            result.summary_file = str(summary_path)
            result.metadata["summary_file"] = result.summary_file
            log(f"Result summary saved to {summary_path}")
        except Exception as storage_exc:
            log(f"Failed to persist result summary: {storage_exc}")

    return result

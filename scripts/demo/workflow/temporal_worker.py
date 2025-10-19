"""
Temporal worker wiring for the single-mutation demo workflow.

This module exposes activity wrappers around the demo helpers, the
RunSingleMutationWorkflow definition, and utilities for starting a worker.
"""
from __future__ import annotations

import asyncio
import traceback
from dataclasses import dataclass
from datetime import timedelta
from pathlib import Path
from typing import Any, Dict, Mapping, Optional

from concurrent.futures import ThreadPoolExecutor
from temporalio import activity, workflow
from temporalio.client import Client
from temporalio.worker import Worker

from scripts.demo.workflow.storage import persist_flow_result
from scripts.demo.workflow.activities import (
    analyze_test_results,
    apply_mutation,
    cleanup_pull_request_and_repo,
    clone_repository,
    commit_and_push_changes,
    create_branch,
    create_pull_request,
    wait_for_checks,
)
from scripts.demo.workflow.flow import MutationFlowResult, generate_mutation_metadata
from scripts.demo.workflow.summary import render_summary_lines


# ---------------------------------------------------------------------------
# Activity input payload definitions


@dataclass
class CloneRepositoryInput:
    repo_url: str
    base_clone_dir: Optional[str] = None


@dataclass
class CreateBranchInput:
    repo_path: str
    branch_name: str


@dataclass
class ApplyMutationInput:
    repo_path: str
    mutation_config: Mapping[str, Any]


@dataclass
class CommitAndPushInput:
    repo_path: str
    branch_name: str
    commit_message: str


@dataclass
class CreatePullRequestInput:
    repo_path: str
    title: str
    body: str
    base_branch: str
    repo_id: Optional[str] = None


@dataclass
class WaitForChecksInput:
    repo_path: str
    pr_number: str
    repo_id: Optional[str]
    timeout_seconds: int


@dataclass
class AnalyzeResultsInput:
    repo_path: str
    pr_results: Mapping[str, Any]
    repo_id: Optional[str]
    output_dir: Optional[str] = None


@dataclass
class CleanupInput:
    repo_path: Optional[str]
    pr_number: Optional[str]
    repo_id: Optional[str]


@dataclass
class PersistResultInput:
    result_data: Dict[str, Any]
    summary_output_dir: Optional[str] = None


@dataclass
class MutationWorkflowParams:
    """Parameters supplied when starting the Temporal workflow."""

    repo_config: Mapping[str, Any]
    timeout_seconds: int = 600
    output_dir: Optional[str] = None
    base_clone_dir: Optional[str] = None
    timestamp: Optional[str] = None
    summary_output_dir: Optional[str] = None


# ---------------------------------------------------------------------------
# Activity implementations


@activity.defn
def clone_repository_activity(payload: CloneRepositoryInput) -> str:
    """Clone the repository and return the local path."""
    activity.logger.info("Cloning repository: %s", payload.repo_url)
    repo_path = clone_repository(payload.repo_url, base_dir=payload.base_clone_dir)
    return str(repo_path)


@activity.defn
def create_branch_activity(payload: CreateBranchInput) -> None:
    """Create or reset the working branch."""
    activity.logger.info("Creating branch %s", payload.branch_name)
    create_branch(Path(payload.repo_path), payload.branch_name)


@activity.defn
def apply_mutation_activity(payload: ApplyMutationInput) -> bool:
    """Apply the mutation and return whether changes were made."""
    activity.logger.info("Applying mutation %s", payload.mutation_config.get("description"))
    return apply_mutation(Path(payload.repo_path), payload.mutation_config)


@activity.defn
def commit_and_push_activity(payload: CommitAndPushInput) -> None:
    """Commit and push the mutated branch."""
    activity.logger.info("Committing and pushing branch %s", payload.branch_name)
    commit_and_push_changes(Path(payload.repo_path), payload.branch_name, payload.commit_message)


@activity.defn
def create_pull_request_activity(payload: CreatePullRequestInput) -> Dict[str, Any]:
    """Open a pull request for the mutated branch."""
    activity.logger.info("Creating pull request: %s", payload.title)
    return create_pull_request(
        Path(payload.repo_path),
        payload.title,
        payload.body,
        base_branch=payload.base_branch,
        repo_id=payload.repo_id,
    )


@activity.defn
def wait_for_checks_activity(payload: WaitForChecksInput) -> Dict[str, Any]:
    """Poll GitHub checks until completion or timeout."""
    activity.logger.info("Waiting for checks on PR #%s", payload.pr_number)
    return wait_for_checks(
        Path(payload.repo_path),
        payload.pr_number,
        timeout_seconds=payload.timeout_seconds,
        repo_id=payload.repo_id,
    )


@activity.defn
def analyze_results_activity(payload: AnalyzeResultsInput) -> Dict[str, Any]:
    """Analyze test results and persist the report."""
    activity.logger.info("Analyzing test results for PR checks")
    analysis, results_file = analyze_test_results(
        Path(payload.repo_path),
        payload.pr_results,
        repo_id=payload.repo_id,
        output_dir=Path(payload.output_dir) if payload.output_dir else None,
    )
    return {
        "analysis": analysis,
        "results_file": str(results_file),
    }


@activity.defn
def cleanup_activity(payload: CleanupInput) -> Dict[str, Any]:
    """Clean up the pull request and repository."""
    repo_path = Path(payload.repo_path) if payload.repo_path else None
    activity.logger.info("Cleaning up repo and PR (pr_number=%s)", payload.pr_number)
    return cleanup_pull_request_and_repo(
        repo_path,
        pr_number=payload.pr_number,
        repo_id=payload.repo_id,
    )


@activity.defn
def persist_result_activity(payload: PersistResultInput) -> str:
    """Persist the workflow result summary to disk."""
    output_path = persist_flow_result(payload.result_data, payload.summary_output_dir)
    activity.logger.info("Result summary stored at %s", output_path)
    return str(output_path)


# ---------------------------------------------------------------------------
# Workflow definition


@workflow.defn
class RunSingleMutationWorkflow:
    """Temporal workflow entry point mirroring the demo mutation flow."""

    @workflow.run
    async def run(self, params: MutationWorkflowParams) -> MutationFlowResult:
        repo_config = params.repo_config
        mutation_config = repo_config["mutation"]
        repo_id = repo_config.get("repo_id")

        # Generate branch and PR metadata deterministically
        if params.timestamp:
            timestamp = params.timestamp
        else:
            timestamp = workflow.now().strftime("%Y%m%d-%H%M%S")
        mutation_metadata = generate_mutation_metadata(mutation_config, timestamp=timestamp)
        branch_name = mutation_metadata["branch_name"]
        pr_title = mutation_metadata["pr_title"]
        pr_body = mutation_metadata["pr_body"]

        result = MutationFlowResult(
            repo_url=repo_config["url"],
            branch_name=branch_name,
            pr_title=pr_title,
            mutation_description=mutation_config["description"],
            metadata={
                "repo_id": repo_id,
                "base_branch": repo_config["base_branch"],
                "timestamp": mutation_metadata["timestamp"],
            },
        )

        repo_path: Optional[str] = None
        pr_number: Optional[str] = None

        try:
            repo_path = await workflow.execute_activity(
                clone_repository_activity,
                CloneRepositoryInput(
                    repo_url=repo_config["url"],
                    base_clone_dir=params.base_clone_dir,
                ),
                schedule_to_close_timeout=timedelta(minutes=5),
            )
            result.repo_path = repo_path
            workflow.logger.info("Repository cloned to %s", repo_path)

            await workflow.execute_activity(
                create_branch_activity,
                CreateBranchInput(repo_path=repo_path, branch_name=branch_name),
                schedule_to_close_timeout=timedelta(minutes=2),
            )
            workflow.logger.info("Branch %s created", branch_name)

            mutation_applied = await workflow.execute_activity(
                apply_mutation_activity,
                ApplyMutationInput(repo_path=repo_path, mutation_config=mutation_config),
                schedule_to_close_timeout=timedelta(minutes=2),
            )
            result.mutation_applied = mutation_applied
            workflow.logger.info("Mutation applied: %s", mutation_applied)

            await workflow.execute_activity(
                commit_and_push_activity,
                CommitAndPushInput(
                    repo_path=repo_path,
                    branch_name=branch_name,
                    commit_message=f"Apply mutation: {mutation_config['description']}",
                ),
                schedule_to_close_timeout=timedelta(minutes=3),
            )
            workflow.logger.info("Branch pushed to origin")

            pr_info = await workflow.execute_activity(
                create_pull_request_activity,
                CreatePullRequestInput(
                    repo_path=repo_path,
                    title=pr_title,
                    body=pr_body,
                    base_branch=repo_config["base_branch"],
                    repo_id=repo_id,
                ),
                schedule_to_close_timeout=timedelta(minutes=3),
            )
            pr_number = pr_info["number"]
            result.pr_number = pr_number
            result.pr_url = pr_info.get("url")
            workflow.logger.info("Pull request created: %s", result.pr_url)

            pr_results = await workflow.execute_activity(
                wait_for_checks_activity,
                WaitForChecksInput(
                    repo_path=repo_path,
                    pr_number=pr_number,
                    repo_id=repo_id,
                    timeout_seconds=params.timeout_seconds,
                ),
                schedule_to_close_timeout=timedelta(seconds=params.timeout_seconds + 60),
            )
            result.pr_results = pr_results
            workflow.logger.info("GitHub checks completed")

            analysis_payload = await workflow.execute_activity(
                analyze_results_activity,
                AnalyzeResultsInput(
                    repo_path=repo_path,
                    pr_results=pr_results,
                    repo_id=repo_id,
                    output_dir=params.output_dir,
                ),
                schedule_to_close_timeout=timedelta(minutes=3),
            )
            result.analysis = analysis_payload["analysis"]
            result.results_file = analysis_payload["results_file"]
            workflow.logger.info("Analysis saved to %s", result.results_file)
        except Exception as exc:
            result.error = str(exc)
            result.traceback = "".join(traceback.format_exception(exc))
            workflow.logger.error("Workflow encountered error: %s", exc)
        finally:
            cleanup_details = await workflow.execute_activity(
                cleanup_activity,
                CleanupInput(
                    repo_path=repo_path,
                    pr_number=pr_number,
                    repo_id=repo_id,
                ),
                schedule_to_close_timeout=timedelta(minutes=5),
            )
            result.cleanup_details = cleanup_details
            workflow.logger.info("Cleanup completed: %s", cleanup_details)

            try:
                summary_path = await workflow.execute_activity(
                    persist_result_activity,
                    PersistResultInput(
                        result_data=result.to_dict(),
                        summary_output_dir=params.summary_output_dir,
                    ),
                    schedule_to_close_timeout=timedelta(minutes=2),
                )
                result.summary_file = summary_path
                result.metadata["summary_file"] = summary_path
                workflow.logger.info("Result summary saved to %s", summary_path)
            except Exception as persist_exc:
                workflow.logger.error("Failed to persist result summary: %s", persist_exc)

        for line in render_summary_lines(repo_config, result):
            workflow.logger.info(line)

        return result


# ---------------------------------------------------------------------------
# Worker bootstrap helper


async def run_worker(
    *,
    task_queue: str,
    temporal_address: str = "localhost:7233",
    namespace: str = "default",
) -> None:
    """Connect to Temporal and start a worker for the demo workflow."""
    client = await Client.connect(temporal_address, namespace=namespace)
    activity_executor = ThreadPoolExecutor()
    try:
        worker = Worker(
            client,
            task_queue=task_queue,
            workflows=[RunSingleMutationWorkflow],
            activities=[
                clone_repository_activity,
                create_branch_activity,
                apply_mutation_activity,
                commit_and_push_activity,
                create_pull_request_activity,
                wait_for_checks_activity,
                analyze_results_activity,
                cleanup_activity,
                persist_result_activity,
            ],
            activity_executor=activity_executor,
        )
        await worker.run()
    finally:
        activity_executor.shutdown(wait=True)


def main() -> None:
    """CLI entry point for running the worker."""
    import argparse

    parser = argparse.ArgumentParser(description="Run Temporal worker for demo mutation workflow")
    parser.add_argument("--task-queue", required=True, help="Temporal task queue to poll")
    parser.add_argument("--address", default="localhost:7233", help="Temporal frontend address (host:port)")
    parser.add_argument("--namespace", default="default", help="Temporal namespace")
    args = parser.parse_args()

    asyncio.run(
        run_worker(
            task_queue=args.task_queue,
            temporal_address=args.address,
            namespace=args.namespace,
        )
    )


if __name__ == "__main__":
    main()

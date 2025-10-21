"""
CLI utility to start the Temporal single-mutation demo workflow.
"""
from __future__ import annotations

import argparse
import asyncio
from datetime import datetime
from typing import Optional

from temporalio.client import Client

from temporal.github.known_repos import KNOWN_REPOS
from temporal.mutation.mutations import get_mutation
from temporal.workflows.mutation_flow import (
    MutationContext,
    MutationFlowResult,
    MutationResult,
    generate_mutation_metadata,
)
from temporal.workflows.temporal_worker import (
    MutationWorkflowParams,
    RunSingleMutationWorkflow,
)
from temporal.workflows.summary import render_summary_lines


async def start_workflow(
    *,
    repo_name: str,
    task_queue: str,
    namespace: str,
    address: str,
    workflow_id: Optional[str],
    timeout_seconds: int,
    output_dir: Optional[str],
    base_clone_dir: Optional[str],
    summary_output_dir: Optional[str],
    wait_for_result: bool,
) -> MutationFlowResult:
    repo_config = KNOWN_REPOS.get(repo_name)
    if not repo_config:
        available = ", ".join(sorted(KNOWN_REPOS.keys()))
        raise ValueError(f"Unknown repository '{repo_name}'. Options: {available}")

    mutation_config = get_mutation(repo_name)
    if not mutation_config:
        available = ", ".join(sorted(KNOWN_REPOS.keys()))
        raise ValueError(
            f"No mutation configured for repository '{repo_name}'. Options: {available}"
        )
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    mutation_metadata = generate_mutation_metadata(mutation_config, timestamp=timestamp)

    params = MutationWorkflowParams(
        repo_config=repo_config,
        timeout_seconds=timeout_seconds,
        output_dir=output_dir,
        base_clone_dir=base_clone_dir,
        timestamp=timestamp,
        summary_output_dir=summary_output_dir,
    )

    client = await Client.connect(address, namespace=namespace)
    handle = await client.start_workflow(
        RunSingleMutationWorkflow.run,
        params,
        id=workflow_id or f"mutation-demo-{timestamp}",
        task_queue=task_queue,
    )

    print(f"Workflow started (id={handle.id}, run_id={handle.run_id})")

    if wait_for_result:
        result = await handle.result()
        print("Workflow completed.")
        for line in render_summary_lines(repo_config, result):
            print(line)
        return result

    interim_context = MutationContext(
        repo_url=repo_config["url"],
        branch_name=mutation_metadata["branch_name"],
        pr_title=mutation_metadata["pr_title"],
        mutation_description=mutation_config["description"],
        repo_id=repo_config.get("repo_id"),
        base_branch=repo_config["base_branch"],
        timestamp=mutation_metadata["timestamp"],
    )
    interim_result = MutationFlowResult(
        context=interim_context,
        outcome=MutationResult(),
    )
    interim_result.workflow.metadata.update(
        {
            "workflow_id": handle.id,
            "run_id": handle.run_id,
        }
    )
    print("Workflow started. Expected branch/PR names:")
    print(f"  - Branch: {interim_result.context.branch_name}")
    print(f"  - PR Title: {interim_result.context.pr_title}")
    if summary_output_dir:
        print(f"  - Summary directory: {summary_output_dir}")
    return interim_result


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Start the Temporal demo mutation workflow")
    parser.add_argument("--repo", default="demo-httpie-cli", help="Demo repository name")
    parser.add_argument("--task-queue", default="mutation-demo-task-queue", help="Temporal task queue")
    parser.add_argument("--namespace", default="default", help="Temporal namespace")
    parser.add_argument("--address", default="localhost:7233", help="Temporal frontend address (host:port)")
    parser.add_argument("--workflow-id", help="Override the workflow ID")
    parser.add_argument("--timeout", type=int, default=600, help="Check wait timeout in seconds")
    parser.add_argument("--output-dir", help="Directory to store analysis artifacts")
    parser.add_argument("--base-clone-dir", help="Override base directory for cloning repos")
    parser.add_argument("--summary-dir", help="Directory to store workflow summary JSON")
    parser.add_argument("--wait", action="store_true", help="Wait for workflow completion and print result")
    return parser.parse_args()


async def main() -> None:
    args = parse_args()
    await start_workflow(
        repo_name=args.repo,
        task_queue=args.task_queue,
        namespace=args.namespace,
        address=args.address,
        workflow_id=args.workflow_id,
        timeout_seconds=args.timeout,
        output_dir=args.output_dir,
        base_clone_dir=args.base_clone_dir,
        summary_output_dir=args.summary_dir,
        wait_for_result=args.wait,
    )


if __name__ == "__main__":
    asyncio.run(main())

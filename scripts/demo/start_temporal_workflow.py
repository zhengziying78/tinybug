"""
CLI utility to start the Temporal single-mutation demo workflow.
"""
from __future__ import annotations

import argparse
import asyncio
from datetime import datetime
from typing import Optional

from temporalio.client import Client

from demo import get_repo_by_name
from flow import MutationFlowResult
from temporal_worker import MutationWorkflowParams, RunSingleMutationWorkflow


def _build_pr_body(mutation_config: dict) -> str:
    return f"""
This PR contains a mutation for testing purposes.

**Mutation Details:**
- File: {mutation_config['file_path']}
- Line: {mutation_config['line_number']}
- Change: `{mutation_config['find_pattern']}` → `{mutation_config['replace_pattern']}`

This mutation tests whether the test suite can detect the change in {mutation_config['description'].lower()}.
"""


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
    wait_for_result: bool,
) -> MutationFlowResult:
    repo_config = get_repo_by_name(repo_name)
    if not repo_config:
        available = ["demo-httpie-cli", "demo-pallets-click", "demo-psf-requests"]
        raise ValueError(f"Unknown repository '{repo_name}'. Options: {', '.join(available)}")

    mutation_config = repo_config["mutation"]
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    branch_name = f"mutation-test-demo-{timestamp}"
    pr_title = f"Mutation Test: {mutation_config['description']} ({timestamp})"
    pr_body = _build_pr_body(mutation_config)

    params = MutationWorkflowParams(
        repo_config=repo_config,
        branch_name=branch_name,
        pr_title=pr_title,
        pr_body=pr_body,
        timeout_seconds=timeout_seconds,
        output_dir=output_dir,
        base_clone_dir=base_clone_dir,
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
        print(result.to_dict())
        return result

    return MutationFlowResult(
        repo_url=repo_config["url"],
        branch_name=branch_name,
        pr_title=pr_title,
        mutation_description=mutation_config["description"],
        metadata={"workflow_id": handle.id, "run_id": handle.run_id},
    )


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
        wait_for_result=args.wait,
    )


if __name__ == "__main__":
    asyncio.run(main())

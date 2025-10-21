"""Main entry point for the mutation testing PoC demo."""
from __future__ import annotations

import sys
import traceback
from dataclasses import replace
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
from models.mutation.context import MutationContext
from models.mutation.result import MutationResult
from temporal.workflows.mutation_flow import MutationFlowResult, generate_mutation_metadata
from temporal.workflows.storage import persist_flow_result
from temporal.workflows.summary import render_summary_lines
from temporal.mutation.mutations import get_mutation
from temporal.github.known_repos import DEFAULT_REPO_NAME, KNOWN_REPOS


def run_single_mutation_flow(
    repo_config: Mapping[str, Any],
    *,
    timeout_seconds: int = 600,
    output_dir: Optional[Path] = None,
    base_clone_dir: Optional[str] = None,
    summary_output_dir: Optional[Path] = None,
    timestamp: Optional[str] = None,
) -> MutationFlowResult:
    """Execute the single-mutation demo workflow and return structured results."""

    mutation_config = get_mutation(repo_config["name"])
    if not mutation_config:
        raise ValueError(f"No mutation configured for repository {repo_config['name']}")

    mutation_metadata = generate_mutation_metadata(mutation_config, timestamp=timestamp)
    branch_name = mutation_metadata["branch_name"]
    pr_title = mutation_metadata["pr_title"]
    pr_body = mutation_metadata["pr_body"]

    context = MutationContext(
        repo_url=repo_config["url"],
        branch_name=branch_name,
        pr_title=pr_title,
        mutation_description=mutation_config["description"],
        repo_id=repo_config.get("repo_id"),
        base_branch=repo_config["base_branch"],
        timestamp=mutation_metadata["timestamp"],
    )
    outcome = MutationResult()
    result = MutationFlowResult(context=context, outcome=outcome)

    repo_path: Optional[Path] = None
    pr_number: Optional[str] = None

    def log(message: str) -> None:
        print(f"[flow] {message}")

    try:
        log(f"Cloning repository {repo_config['url']}")
        repo_path = clone_repository(repo_config["url"], base_dir=base_clone_dir)
        result.workflow.repo_path = str(repo_path)

        log(f"Creating branch {branch_name}")
        create_branch(repo_path, branch_name)

        log("Applying mutation")
        mutation_applied = apply_mutation(repo_path, mutation_config)
        result.outcome.mutation_applied = mutation_applied
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
            base_branch=repo_config["base_branch"],
            repo_id=repo_config.get("repo_id"),
        )
        pr_number = pr_info["number"]
        pr_url = pr_info.get("url")
        result.context = replace(result.context, pr_number=pr_number, pr_url=pr_url)
        result.outcome.pr_number = pr_number
        result.outcome.pr_url = pr_url
        log(f"Pull request created: {pr_url}")

        log("Waiting for GitHub checks to complete")
        pr_results = wait_for_checks(
            repo_path,
            pr_number,
            timeout_seconds=timeout_seconds,
            repo_id=repo_config.get("repo_id"),
        )
        result.outcome.pr_results = pr_results
        log("Checks completed")

        log("Analyzing test results")
        analysis, results_file = analyze_test_results(
            repo_path,
            pr_results,
            repo_id=repo_config.get("repo_id"),
            output_dir=output_dir,
        )
        result.outcome.analysis = analysis
        result.outcome.results_file = str(results_file)
        log(f"Analysis saved to {result.outcome.results_file}")
    except Exception as exc:  # pragma: no cover - CLI side-effect logging
        result.outcome.error = str(exc)
        result.outcome.traceback = traceback.format_exc()
        log(f"Encountered error: {exc}")
    finally:
        log("Cleaning up repository and pull request")
        cleanup_details = cleanup_pull_request_and_repo(
            repo_path,
            pr_number=pr_number,
            repo_id=repo_config.get("repo_id"),
        )
        result.workflow.cleanup_details = cleanup_details

        try:
            summary_path = persist_flow_result(
                result.to_dict(),
                summary_output_dir,
            )
            result.outcome.summary_file = str(summary_path)
            result.workflow.metadata["summary_file"] = result.outcome.summary_file
            log(f"Result summary saved to {summary_path}")
        except Exception as storage_exc:  # pragma: no cover - CLI side-effect logging
            log(f"Failed to persist result summary: {storage_exc}")

    return result


def select_repo_with_timeout():
    """Select a repository with a 10-second timeout."""
    import threading
    from queue import Queue, Empty
    
    print("Available repositories for mutation testing:")
    print()
    menu_entries = list(KNOWN_REPOS.items())
    choice_map = {str(index): name for index, (name, _) in enumerate(menu_entries, start=1)}

    for index, (name, repo) in enumerate(menu_entries, start=1):
        mutation = get_mutation(name)
        mutation_desc = mutation["description"] if mutation else "None configured"
        print(f"{index}. {repo['name']}")
        print(f"   URL: {repo['url']}")
        print(f"   Mutation: {mutation_desc}")
        print()
    
    print(
        f"Enter your choice (1-{len(menu_entries)}) or wait 10 seconds for default ({DEFAULT_REPO_NAME}):"
    )
    
    # Use a queue to communicate between threads
    input_queue = Queue()
    
    def get_input():
        try:
            user_input = input().strip()
            input_queue.put(user_input)
        except (KeyboardInterrupt, EOFError):
            input_queue.put(None)
    
    # Start input thread
    input_thread = threading.Thread(target=get_input)
    input_thread.daemon = True
    input_thread.start()
    
    # Countdown with input checking
    choice = None
    for i in range(10, 0, -1):
        print(f"\rDefaulting to {DEFAULT_REPO_NAME} in {i} seconds... ", end='', flush=True)
        
        # Check for input
        try:
            user_input = input_queue.get(timeout=1)
            print(f"\rUser input received: {user_input}                    ")
            if user_input in choice_map:
                choice = choice_map[user_input]
            elif user_input in KNOWN_REPOS:
                choice = user_input
            elif user_input == "":
                # Empty input (Enter pressed) means use default
                choice = DEFAULT_REPO_NAME
            else:
                choice = DEFAULT_REPO_NAME
            break
        except Empty:
            continue
    
    # If no input received, use default
    if choice is None:
        print(f"\rTime's up! Using default: {DEFAULT_REPO_NAME}                ")
        choice = DEFAULT_REPO_NAME
    
    selected_repo = KNOWN_REPOS[choice]
    print(f"\nSelected: {selected_repo['name']}")
    return selected_repo


def main():
    """Main function to run the mutation testing demo."""
    print("Starting mutation testing PoC demo...")
    print()
    
    # Select repository
    if len(sys.argv) > 1:
        repo_name = sys.argv[1]
        selected_repo = KNOWN_REPOS.get(repo_name)
        if selected_repo:
            print(f"Using repository from command line: {selected_repo['name']}")
        else:
            print(f"Error: Unknown repository name '{repo_name}'")
            print("Available repositories: demo-httpie-cli, demo-pallets-click, demo-psf-requests")
            sys.exit(1)
    else:
        selected_repo = select_repo_with_timeout()
    
    # Generate timestamp and create dynamic names
    result = run_single_mutation_flow(
        selected_repo,
        timeout_seconds=600,
    )

    print()
    for line in render_summary_lines(selected_repo, result):
        print(line)
    print("Demo completed!")


if __name__ == "__main__":
    main()

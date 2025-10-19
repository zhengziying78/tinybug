"""
Main entry point for mutation testing PoC demo.

Usage: python demo.py [repo_name]
  repo_name: demo-httpie-cli, demo-pallets-click, or demo-psf-requests
"""
import json
import sys
from pathlib import Path
from datetime import datetime
from mutation.mutations import get_mutation
from flow import run_single_mutation_flow


# Configuration - repo options
REPO_OPTIONS = {
    "1": {
        "name": "demo-httpie-cli",
        "url": "https://github.com/zhengziying78/demo-httpie-cli",
        "base_branch": "master",
        "repo_id": "zhengziying78/demo-httpie-cli",
        "mutation": get_mutation("demo-httpie-cli")
    },
    "2": {
        "name": "demo-pallets-click",
        "url": "https://github.com/zhengziying78/demo-pallets-click",
        "base_branch": "main",
        "repo_id": "zhengziying78/demo-pallets-click",
        "mutation": get_mutation("demo-pallets-click")
    },
    "3": {
        "name": "demo-psf-requests",
        "url": "https://github.com/zhengziying78/demo-psf-requests",
        "base_branch": "main",
        "repo_id": "zhengziying78/demo-psf-requests",
        "mutation": get_mutation("demo-psf-requests")
    }
}

DEFAULT_CHOICE = "1"  # demo-httpie-cli


def select_repo_with_timeout():
    """Select a repository with a 10-second timeout."""
    import threading
    from queue import Queue, Empty
    
    print("Available repositories for mutation testing:")
    print()
    for key, repo in REPO_OPTIONS.items():
        print(f"{key}. {repo['name']}")
        print(f"   URL: {repo['url']}")
        print(f"   Mutation: {repo['mutation']['description']}")
        print()
    
    print(f"Enter your choice (1-{len(REPO_OPTIONS)}) or wait 10 seconds for default (demo-httpie-cli):")
    
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
        print(f"\rDefaulting to demo-httpie-cli in {i} seconds... ", end='', flush=True)
        
        # Check for input
        try:
            user_input = input_queue.get(timeout=1)
            print(f"\rUser input received: {user_input}                    ")
            if user_input in REPO_OPTIONS:
                choice = user_input
            elif user_input == "":
                # Empty input (Enter pressed) means use default
                choice = DEFAULT_CHOICE
            else:
                choice = DEFAULT_CHOICE
            break
        except Empty:
            continue
    
    # If no input received, use default
    if choice is None:
        print(f"\rTime's up! Using default: demo-httpie-cli                ")
        choice = DEFAULT_CHOICE
    
    selected_repo = REPO_OPTIONS[choice]
    print(f"\nSelected: {selected_repo['name']}")
    return selected_repo


def get_repo_by_name(repo_name):
    """Get repository configuration by name."""
    # Map repo names to their keys
    repo_name_to_key = {
        "demo-httpie-cli": "1",
        "demo-pallets-click": "2", 
        "demo-psf-requests": "3"
    }
    
    if repo_name in repo_name_to_key:
        key = repo_name_to_key[repo_name]
        return REPO_OPTIONS[key]
    else:
        return None


def main():
    """Main function to run the mutation testing demo."""
    print("Starting mutation testing PoC demo...")
    print()
    
    # Step 0: Select repository
    if len(sys.argv) > 1:
        repo_name = sys.argv[1]
        selected_repo = get_repo_by_name(repo_name)
        if selected_repo:
            print(f"Using repository from command line: {selected_repo['name']}")
        else:
            print(f"Error: Unknown repository name '{repo_name}'")
            print("Available repositories: demo-httpie-cli, demo-pallets-click, demo-psf-requests")
            sys.exit(1)
    else:
        selected_repo = select_repo_with_timeout()
    
    mutation_config = selected_repo["mutation"]
    
    # Generate timestamp and create dynamic names
    timestamp = datetime.now().strftime('%Y%m%d-%H%M%S')
    branch_name = f"mutation-test-demo-{timestamp}"
    pr_title = f"Mutation Test: {mutation_config['description']} ({timestamp})"
    pr_body = f"""
This PR contains a mutation for testing purposes.

**Mutation Details:**
- File: {mutation_config['file_path']}
- Line: {mutation_config['line_number']}
- Change: `{mutation_config['find_pattern']}` → `{mutation_config['replace_pattern']}`

This mutation tests whether the test suite can detect the change in {mutation_config['description'].lower()}.
"""
    
    result = run_single_mutation_flow(
        selected_repo,
        branch_name=branch_name,
        pr_title=pr_title,
        pr_body=pr_body,
        timeout_seconds=600,
    )
    
    print()
    print("Mutation testing summary:")
    print(f"  - Repository: {selected_repo['url']}")
    print(f"  - Branch: {branch_name}")
    print(f"  - Pull request: {result.pr_url or 'N/A'}")
    print(f"  - Mutation applied: {result.mutation_applied}")
    
    if result.analysis:
        summary = result.analysis.get('summary', {})
        print(f"  - Total checks: {summary.get('total_checks', 0)}")
        print(f"  - Passed checks: {summary.get('passed_checks', 0)}")
        print(f"  - Failed checks: {summary.get('failed_checks', 0)}")
        print(f"  - Mutation killed: {summary.get('mutation_killed', False)}")
        print(f"  - Mutation survived: {summary.get('mutation_survived', False)}")
        print(f"  - Results file: {result.results_file}")
        
        if result.analysis.get('test_failures'):
            print()
            print("Detailed failure information:")
            for failure in result.analysis['test_failures']:
                check_name = failure.get('check_name', 'Unknown')
                failure_reason = failure.get('failure_reason', 'due to unknown reasons')
                failed_tests = failure.get('failed_tests', [])
                
                print(f"  • {check_name}: {failure_reason}")
                
                if failed_tests:
                    print("    Failed tests:")
                    for test in failed_tests:
                        print(f"      - {test}")
                print()
    else:
        print("  - No analysis available")
    
    if result.error:
        print()
        print("Errors encountered during workflow:")
        print(f"  - {result.error}")
        if result.traceback:
            print(result.traceback)
    
    print()
    print(f"Cleanup results: {result.cleanup_details}")
    print("Demo completed!")


if __name__ == "__main__":
    main()

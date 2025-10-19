"""
Main entry point for mutation testing PoC demo.

Usage: python demo.py [repo_name]
  repo_name: demo-httpie-cli, demo-pallets-click, or demo-psf-requests
"""
import sys
from flow import run_single_mutation_flow
from known_repos import DEFAULT_REPO_NAME, KNOWN_REPOS, repo_menu_entries


def select_repo_with_timeout():
    """Select a repository with a 10-second timeout."""
    import threading
    from queue import Queue, Empty
    
    print("Available repositories for mutation testing:")
    print()
    menu_entries = repo_menu_entries()
    choice_map = {str(index): name for index, (name, _) in enumerate(menu_entries, start=1)}

    for index, (name, repo) in enumerate(menu_entries, start=1):
        print(f"{index}. {repo['name']}")
        print(f"   URL: {repo['url']}")
        print(f"   Mutation: {repo['mutation']['description']}")
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


def print_mutation_summary(selected_repo, result):
    """Print summary information for the mutation testing run."""
    print()
    print("Mutation testing summary:")
    print(f"  - Repository: {selected_repo['url']}")
    print(f"  - Branch: {result.branch_name}")
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
    
    mutation_config = selected_repo["mutation"]
    
    # Generate timestamp and create dynamic names
    result = run_single_mutation_flow(
        selected_repo,
        timeout_seconds=600,
    )
    
    print_mutation_summary(selected_repo, result)
    
    print()
    print(f"Cleanup results: {result.cleanup_details}")
    print("Demo completed!")


if __name__ == "__main__":
    main()

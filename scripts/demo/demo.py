"""
Main entry point for mutation testing PoC demo.

Usage: python demo.py
"""
import json
from pathlib import Path
from datetime import datetime
from repo_manager import RepoManager
from mutator import Mutator, MutationSpec
from pr_manager import PRManager
from test_analyzer import TestAnalyzer
from cleanup import CleanupManager


# Configuration - repo options
REPO_OPTIONS = {
    "1": {
        "name": "demo-httpie-cli",
        "url": "https://github.com/zhengziying78/demo-httpie-cli",
        "base_branch": "master",
        "repo_id": "zhengziying78/demo-httpie-cli",
        "mutation": {
            "file_path": "httpie/cli/dicts.py",
            "line_number": 26,
            "find_pattern": r"if value is None:",
            "replace_pattern": "if not value is None:",
            "description": "Change None check logic"
        }
    },
    "2": {
        "name": "demo-pallets-click",
        "url": "https://github.com/zhengziying78/demo-pallets-click",
        "base_branch": "main",
        "repo_id": "zhengziying78/demo-pallets-click",
        "mutation": {
            "file_path": "src/click/utils.py",
            "line_number": 126,
            "find_pattern": r"self.encoding = encoding",
            "replace_pattern": "self.encoding = \"utf-16\"",
            "description": "Change encoding assignment"
        }
    },
    "3": {
        "name": "demo-psf-requests",
        "url": "https://github.com/zhengziying78/demo-psf-requests",
        "base_branch": "main",
        "repo_id": "zhengziying78/demo-psf-requests",
        "mutation": {
            "file_path": "src/requests/status_codes.py",
            "line_number": 87,
            "find_pattern": r'444: \("no_response", "none"\),',
            "replace_pattern": '444: ("no_response", "no"),',
            "description": "Change status code description"
        }
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
            if user_input and user_input in REPO_OPTIONS:
                choice = user_input
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


def main():
    """Main function to run the mutation testing demo."""
    print("Starting mutation testing PoC demo...")
    print()
    
    # Step 0: Select repository
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
    
    # Initialize managers
    repo_manager = RepoManager()
    test_analyzer = TestAnalyzer()
    cleanup_manager = CleanupManager()
    
    repo_path = None
    pr_number = None
    
    try:
        # Step 1: Clone the repository
        print(f"Cloning repository: {selected_repo['url']}")
        repo_path = repo_manager.clone_repo(selected_repo['url'])
        print(f"Repository cloned to: {repo_path}")
        
        # Step 2: Create a branch for mutation
        print(f"Creating branch: {branch_name}")
        repo_manager.create_branch(repo_path, branch_name)
        
        # Step 3: Apply mutation
        print("Applying mutation...")
        mutator = Mutator(repo_path)
        mutation_spec = MutationSpec(
            file_path=mutation_config["file_path"],
            line_number=mutation_config["line_number"],
            find_pattern=mutation_config["find_pattern"],
            replace_pattern=mutation_config["replace_pattern"]
        )
        
        mutation_applied = mutator.apply_mutation(mutation_spec)
        if mutation_applied:
            print("Mutation applied successfully")
        else:
            print("Warning: No changes made during mutation")
        
        # Step 4: Commit and push changes
        print("Committing changes...")
        repo_manager.commit_changes(repo_path, f"Apply mutation: {mutation_config['description']}")
        repo_manager.push_branch(repo_path, branch_name)
        
        # Step 5: Create pull request
        print("Creating pull request...")
        pr_manager = PRManager(repo_path)
        pr_info = pr_manager.create_pull_request(pr_title, pr_body, base_branch=selected_repo['base_branch'], repo=selected_repo['repo_id'])
        pr_number = pr_info["number"]
        print(f"Pull request created: {pr_info['url']}")
        
        # Step 6: Wait for and analyze test results
        print("Waiting for test results...")
        pr_results = pr_manager.wait_for_checks(pr_number, timeout_seconds=600, repo=selected_repo['repo_id'])  # 10 minutes timeout
        
        # Step 7: Analyze and save results
        print("Analyzing test results...")
        analysis = test_analyzer.analyze_pr_results(pr_results)
        results_file = test_analyzer.save_results(analysis)
        
        print(f"Test results saved to: {results_file}")
        print(f"Mutation testing summary:")
        print(f"  - Total checks: {analysis['summary']['total_checks']}")
        print(f"  - Passed checks: {analysis['summary']['passed_checks']}")
        print(f"  - Failed checks: {analysis['summary']['failed_checks']}")
        print(f"  - Mutation killed: {analysis['summary']['mutation_killed']}")
        print(f"  - Mutation survived: {analysis['summary']['mutation_survived']}")
        
    except Exception as e:
        print(f"Error during execution: {str(e)}")
        
    finally:
        # Step 8: Cleanup
        print("Cleaning up...")
        if repo_path and pr_number:
            cleanup_results = cleanup_manager.cleanup_pr_and_repo(repo_path, pr_number, selected_repo['repo_id'])
            print(f"Cleanup results: {cleanup_results}")
        elif repo_path:
            # Clean up repo even if PR wasn't created
            repo_manager.cleanup_repo(repo_path)
            print("Repository cleaned up")
        
        print("Demo completed!")


if __name__ == "__main__":
    main()
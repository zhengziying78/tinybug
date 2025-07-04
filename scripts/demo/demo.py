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


# Configuration - hardcoded for demo
REPO_URL = "https://github.com/zhengziying78/demo-httpie-cli"
MUTATION_CONFIG = {
    "file_path": "httpie/cli/dicts.py",
    "line_number": 26,
    "find_pattern": r"if value is None:",
    "replace_pattern": "if not value is None:"
}
BRANCH_NAME = f"mutation-test-demo-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
PR_TITLE = "Mutation Test: Change None check logic"
PR_BODY = """
This PR contains a mutation for testing purposes.

**Mutation Details:**
- File: httpie/cli/dicts.py
- Line: 26
- Change: `if value is None:` → `if not value is None:`

This mutation tests whether the test suite can detect the logical change in None checking.
"""


def main():
    """Main function to run the mutation testing demo."""
    print("Starting mutation testing PoC demo...")
    
    # Initialize managers
    repo_manager = RepoManager()
    test_analyzer = TestAnalyzer()
    cleanup_manager = CleanupManager()
    
    repo_path = None
    pr_number = None
    
    try:
        # Step 1: Clone the repository
        print(f"Cloning repository: {REPO_URL}")
        repo_path = repo_manager.clone_repo(REPO_URL)
        print(f"Repository cloned to: {repo_path}")
        
        # Step 2: Create a branch for mutation
        print(f"Creating branch: {BRANCH_NAME}")
        repo_manager.create_branch(repo_path, BRANCH_NAME)
        
        # Step 3: Apply mutation
        print("Applying mutation...")
        mutator = Mutator(repo_path)
        mutation_spec = MutationSpec(
            file_path=MUTATION_CONFIG["file_path"],
            line_number=MUTATION_CONFIG["line_number"],
            find_pattern=MUTATION_CONFIG["find_pattern"],
            replace_pattern=MUTATION_CONFIG["replace_pattern"]
        )
        
        mutation_applied = mutator.apply_mutation(mutation_spec)
        if mutation_applied:
            print("Mutation applied successfully")
        else:
            print("Warning: No changes made during mutation")
        
        # Step 4: Commit and push changes
        print("Committing changes...")
        repo_manager.commit_changes(repo_path, "Apply mutation: Change None check logic")
        repo_manager.push_branch(repo_path, BRANCH_NAME)
        
        # Step 5: Create pull request
        print("Creating pull request...")
        pr_manager = PRManager(repo_path)
        pr_info = pr_manager.create_pull_request(PR_TITLE, PR_BODY, base_branch="master", repo="zhengziying78/demo-httpie-cli")
        pr_number = pr_info["number"]
        print(f"Pull request created: {pr_info['url']}")
        
        # Step 6: Wait for and analyze test results
        print("Waiting for test results...")
        pr_results = pr_manager.wait_for_checks(pr_number, timeout_seconds=600)  # 10 minutes timeout
        
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
            cleanup_results = cleanup_manager.cleanup_pr_and_repo(repo_path, pr_number)
            print(f"Cleanup results: {cleanup_results}")
        elif repo_path:
            # Clean up repo even if PR wasn't created
            repo_manager.cleanup_repo(repo_path)
            print("Repository cleaned up")
        
        print("Demo completed!")


if __name__ == "__main__":
    main()
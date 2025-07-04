"""
Cleanup functionality for mutation testing PoC.
"""
from pathlib import Path
from typing import List, Dict, Any
from repo_manager import RepoManager
from pr_manager import PRManager


class CleanupManager:
    def __init__(self):
        self.repo_manager = RepoManager()
    
    def cleanup_pr_and_repo(self, repo_path: Path, pr_number: str) -> Dict[str, Any]:
        """Clean up pull request and local repository."""
        cleanup_results = {
            'pr_closed': False,
            'repo_deleted': False,
            'errors': []
        }
        
        try:
            # Close the pull request
            pr_manager = PRManager(repo_path)
            pr_manager.close_pull_request(pr_number)
            cleanup_results['pr_closed'] = True
        except Exception as e:
            cleanup_results['errors'].append(f"Failed to close PR: {str(e)}")
        
        try:
            # Delete the local repository
            self.repo_manager.cleanup_repo(repo_path)
            cleanup_results['repo_deleted'] = True
        except Exception as e:
            cleanup_results['errors'].append(f"Failed to delete repo: {str(e)}")
        
        return cleanup_results
    
    def cleanup_multiple_repos(self, cleanup_items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Clean up multiple repositories and PRs."""
        results = []
        
        for item in cleanup_items:
            repo_path = Path(item['repo_path'])
            pr_number = item['pr_number']
            
            result = self.cleanup_pr_and_repo(repo_path, pr_number)
            result['repo_path'] = str(repo_path)
            result['pr_number'] = pr_number
            results.append(result)
        
        return results
"""
Pull request management functionality for mutation testing PoC.
"""
import subprocess
import json
from pathlib import Path
from typing import Dict, Any, Optional


class PRManager:
    def __init__(self, repo_path: Path):
        self.repo_path = repo_path
    
    def create_pull_request(self, title: str, body: str, base_branch: str = "main", repo: str = None) -> Dict[str, Any]:
        """Create a pull request using GitHub CLI."""
        cmd = [
            "gh", "pr", "create",
            "--title", title,
            "--body", body,
            "--base", base_branch
        ]
        
        # If repo is specified, add it to target the correct repository
        if repo:
            cmd.extend(["--repo", repo])
        
        result = subprocess.run(cmd, cwd=self.repo_path, capture_output=True, text=True, check=True)
        pr_url = result.stdout.strip()
        
        # Get PR number from URL
        pr_number = pr_url.split("/")[-1]
        
        return {
            "url": pr_url,
            "number": pr_number
        }
    
    def get_pr_status(self, pr_number: str) -> Dict[str, Any]:
        """Get the status of a pull request."""
        cmd = [
            "gh", "pr", "view", pr_number, "--json", 
            "number,title,state,mergeable,statusCheckRollup,url"
        ]
        
        result = subprocess.run(cmd, cwd=self.repo_path, capture_output=True, text=True, check=True)
        return json.loads(result.stdout)
    
    def get_pr_checks(self, pr_number: str) -> Dict[str, Any]:
        """Get the check results for a pull request."""
        cmd = [
            "gh", "pr", "checks", pr_number, "--json"
        ]
        
        result = subprocess.run(cmd, cwd=self.repo_path, capture_output=True, text=True, check=True)
        return json.loads(result.stdout)
    
    def close_pull_request(self, pr_number: str) -> None:
        """Close a pull request without merging."""
        cmd = ["gh", "pr", "close", pr_number]
        subprocess.run(cmd, cwd=self.repo_path, check=True)
    
    def wait_for_checks(self, pr_number: str, timeout_seconds: int = 300) -> Dict[str, Any]:
        """Wait for PR checks to complete and return results."""
        import time
        
        start_time = time.time()
        
        while time.time() - start_time < timeout_seconds:
            try:
                status = self.get_pr_status(pr_number)
                checks = self.get_pr_checks(pr_number)
                
                # Check if all checks are completed
                if status.get('statusCheckRollup'):
                    rollup = status['statusCheckRollup']
                    if rollup.get('state') in ['SUCCESS', 'FAILURE', 'ERROR']:
                        return {
                            'status': status,
                            'checks': checks,
                            'completed': True
                        }
                
                time.sleep(30)  # Wait 30 seconds before checking again
                
            except subprocess.CalledProcessError:
                # Continue trying if there's an error
                time.sleep(30)
                continue
        
        # Timeout reached
        return {
            'status': self.get_pr_status(pr_number),
            'checks': self.get_pr_checks(pr_number),
            'completed': False,
            'timeout': True
        }
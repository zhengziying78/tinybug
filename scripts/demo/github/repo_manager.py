"""
Repository management functionality for mutation testing PoC.
"""
import os
import shutil
import subprocess
from pathlib import Path
from typing import Optional


class RepoManager:
    def __init__(self, base_dir: str = "~/Repos"):
        self.base_dir = Path(base_dir).expanduser()
        self.base_dir.mkdir(parents=True, exist_ok=True)
    
    def clone_repo(self, repo_url: str) -> Path:
        """Clone a GitHub repository to the base directory."""
        repo_name = repo_url.split("/")[-1]
        if repo_name.endswith(".git"):
            repo_name = repo_name[:-4]
        
        repo_path = self.base_dir / repo_name
        
        # Remove existing clone if it exists
        if repo_path.exists():
            shutil.rmtree(repo_path)
        
        # Clone the repository
        subprocess.run([
            "git", "clone", repo_url, str(repo_path)
        ], check=True)
        
        return repo_path
    
    def cleanup_repo(self, repo_path: Path) -> None:
        """Remove the cloned repository."""
        if repo_path.exists():
            shutil.rmtree(repo_path)
    
    def create_branch(self, repo_path: Path, branch_name: str) -> None:
        """Create and checkout a new branch in the repository."""
        # First, try to delete the branch if it exists locally
        try:
            subprocess.run([
                "git", "branch", "-D", branch_name
            ], cwd=repo_path, check=False)
        except subprocess.CalledProcessError:
            pass  # Branch doesn't exist locally, that's fine
        
        # Create and checkout the new branch
        subprocess.run([
            "git", "checkout", "-b", branch_name
        ], cwd=repo_path, check=True)
    
    def commit_changes(self, repo_path: Path, message: str) -> None:
        """Commit all changes in the repository."""
        subprocess.run([
            "git", "add", "."
        ], cwd=repo_path, check=True)
        
        subprocess.run([
            "git", "commit", "-m", message
        ], cwd=repo_path, check=True)
    
    def push_branch(self, repo_path: Path, branch_name: str) -> None:
        """Push the branch to origin."""
        # First, try to delete the remote branch if it exists
        try:
            subprocess.run([
                "git", "push", "origin", "--delete", branch_name
            ], cwd=repo_path, check=False, capture_output=True)
        except subprocess.CalledProcessError:
            pass  # Branch doesn't exist on remote, that's fine
        
        # Push the branch to origin
        subprocess.run([
            "git", "push", "-u", "origin", branch_name
        ], cwd=repo_path, check=True)
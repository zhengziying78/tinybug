#!/usr/bin/env python3
"""
Cleanup GitHub pull requests in demo repositories.

This script closes all open pull requests in the three demo repositories:
- https://github.com/zhengziying78/demo-httpie-cli
- https://github.com/zhengziying78/demo-pallets-click
- https://github.com/zhengziying78/demo-psf-requests
"""

import subprocess
import json
import sys
from typing import List, Dict, Any


def run_gh_command(cmd: List[str]) -> Dict[str, Any]:
    """Run a GitHub CLI command and return the result."""
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        return {"success": True, "output": result.stdout.strip(), "error": None}
    except subprocess.CalledProcessError as e:
        return {"success": False, "output": None, "error": e.stderr.strip()}


def get_open_prs(repo: str) -> List[Dict[str, Any]]:
    """Get all open pull requests for a repository."""
    cmd = [
        "gh", "pr", "list", 
        "--repo", repo,
        "--state", "open",
        "--json", "number,title,headRefName"
    ]
    
    result = run_gh_command(cmd)
    if result["success"]:
        try:
            return json.loads(result["output"])
        except json.JSONDecodeError:
            print(f"Failed to parse JSON response for {repo}")
            return []
    else:
        print(f"Failed to get PRs for {repo}: {result['error']}")
        return []


def close_pr(repo: str, pr_number: int) -> bool:
    """Close a pull request."""
    cmd = ["gh", "pr", "close", str(pr_number), "--repo", repo]
    
    result = run_gh_command(cmd)
    if result["success"]:
        print(f"✅ Closed PR #{pr_number} in {repo}")
        return True
    else:
        print(f"❌ Failed to close PR #{pr_number} in {repo}: {result['error']}")
        return False


def main():
    """Main cleanup function."""
    repositories = [
        "https://github.com/zhengziying78/demo-httpie-cli",
        "https://github.com/zhengziying78/demo-pallets-click",
        "https://github.com/zhengziying78/demo-psf-requests"
    ]
    
    print("🧹 Starting GitHub pull request cleanup...")
    print(f"Target repositories: {len(repositories)}")
    print()
    
    total_closed = 0
    total_failed = 0
    
    for repo_url in repositories:
        # Extract repo name from URL
        repo_name = repo_url.split("github.com/")[-1]
        
        print(f"📋 Checking {repo_name}...")
        
        # Get open PRs
        open_prs = get_open_prs(repo_name)
        
        if not open_prs:
            print(f"   No open pull requests found")
            print()
            continue
        
        print(f"   Found {len(open_prs)} open pull request(s)")
        
        # Close each PR
        for pr in open_prs:
            pr_number = pr["number"]
            pr_title = pr["title"]
            branch_name = pr["headRefName"]
            
            print(f"   🗑️  Closing PR #{pr_number}: {pr_title} (branch: {branch_name})")
            
            if close_pr(repo_name, pr_number):
                total_closed += 1
            else:
                total_failed += 1
        
        print()
    
    # Summary
    print("📊 Cleanup Summary:")
    print(f"   ✅ Pull requests closed: {total_closed}")
    if total_failed > 0:
        print(f"   ❌ Failed to close: {total_failed}")
    
    if total_failed > 0:
        print("\n⚠️  Some pull requests could not be closed. Please check the error messages above.")
        sys.exit(1)
    else:
        print("\n🎉 All pull requests have been successfully closed!")


if __name__ == "__main__":
    main()
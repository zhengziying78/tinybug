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
    
    def get_pr_status(self, pr_number: str, repo: str = None) -> Dict[str, Any]:
        """Get the status of a pull request."""
        cmd = [
            "gh", "pr", "view", pr_number, "--json", 
            "number,title,state,mergeable,statusCheckRollup,url"
        ]
        
        # Add repo parameter if specified
        if repo:
            cmd.extend(["--repo", repo])
        
        result = subprocess.run(cmd, cwd=self.repo_path, capture_output=True, text=True, check=True)
        return json.loads(result.stdout)
    
    def get_pr_checks(self, pr_number: str, repo: str = None) -> Dict[str, Any]:
        """Get the check results for a pull request."""
        cmd = [
            "gh", "pr", "checks", pr_number, "--json", 
            "name,state,bucket,completedAt,startedAt,description,link,workflow"
        ]
        
        # Add repo parameter if specified
        if repo:
            cmd.extend(["--repo", repo])
        
        try:
            result = subprocess.run(cmd, cwd=self.repo_path, capture_output=True, text=True, check=True)
            return json.loads(result.stdout)
        except subprocess.CalledProcessError as e:
            # If exit code is 8, it means checks are pending
            if e.returncode == 8:
                return []  # No checks available yet
            # Handle the case where no checks are reported on the branch yet
            if e.stderr and "no checks reported on the" in e.stderr.lower():
                return []  # Checks haven't started yet
            # For other errors, check if there are simply no checks configured
            if e.stderr and ("No checks reported" in e.stderr or "not found" in e.stderr.lower()):
                return []  # No checks configured
            # Print detailed error information for debugging
            print(f"DEBUG: gh pr checks failed with return code {e.returncode}")
            print(f"DEBUG: stderr: {e.stderr}")
            print(f"DEBUG: stdout: {e.stdout}")
            raise  # Re-raise for other errors
    
    def close_pull_request(self, pr_number: str, repo: str = None) -> None:
        """Close a pull request without merging."""
        cmd = ["gh", "pr", "close", pr_number]
        
        # Add repo parameter if specified
        if repo:
            cmd.extend(["--repo", repo])
        
        subprocess.run(cmd, cwd=self.repo_path, check=True)
    
    def wait_for_checks(self, pr_number: str, timeout_seconds: int = 300, repo: str = None) -> Dict[str, Any]:
        """Wait for PR checks to complete and return results."""
        import time
        
        start_time = time.time()
        
        while time.time() - start_time < timeout_seconds:
            try:
                status = self.get_pr_status(pr_number, repo)
                checks = self.get_pr_checks(pr_number, repo)
                
                # Print detailed status information
                elapsed_time = int(time.time() - start_time)
                print(f"⏱️  Waiting for checks... ({elapsed_time}s elapsed)")
                
                # Defensive programming: ensure status is a dict
                if not isinstance(status, dict):
                    print(f"🔍 Unexpected status type: {type(status)}, retrying...")
                    time.sleep(15)
                    continue
                
                # Analyze rollup status
                if status.get('statusCheckRollup'):
                    rollup = status['statusCheckRollup']
                    rollup_state = rollup.get('state', 'UNKNOWN')
                    print(f"📊 Overall status: {rollup_state}")
                    
                    if rollup.get('state') in ['SUCCESS', 'FAILURE', 'ERROR']:
                        print(f"✅ All checks completed with status: {rollup_state}")
                        return {
                            'status': status,
                            'checks': checks,
                            'completed': True
                        }
                else:
                    print("📊 Overall status: PENDING (no rollup data yet)")
                
                # Analyze individual checks
                if checks and isinstance(checks, list) and len(checks) > 0:
                    total_checks = len(checks)
                    # Use 'bucket' field: pass, fail, pending, skipping, cancel
                    completed_checks = sum(1 for check in checks if check.get('bucket') in ['pass', 'fail', 'cancel', 'skipping'])
                    running_checks = sum(1 for check in checks if check.get('bucket') in ['pending'])
                    passed_checks = sum(1 for check in checks if check.get('bucket') == 'pass')
                    failed_checks = sum(1 for check in checks if check.get('bucket') == 'fail')
                    
                    print(f"🔍 Checks summary: {total_checks} total, {completed_checks} completed, {running_checks} running")
                    print(f"   ✅ Passed: {passed_checks}, ❌ Failed: {failed_checks}")
                    
                    # Show individual check details (limit to first 10 to avoid spam)
                    checks_to_show = checks[:10]
                    for check in checks_to_show:
                        check_name = check.get('name', 'Unknown')
                        check_state = check.get('state', 'unknown')
                        check_bucket = check.get('bucket', '')
                        if check_bucket:
                            print(f"   • {check_name}: {check_state} ({check_bucket})")
                        else:
                            print(f"   • {check_name}: {check_state}")
                    
                    if len(checks) > 10:
                        print(f"   ... and {len(checks) - 10} more checks")
                else:
                    print("🔍 No checks available yet - GitHub Actions may still be starting up")
                    # If no checks are available, wait a bit longer for them to start
                    if elapsed_time > 120:  # Wait 2 minutes to see if checks start
                        print("🔍 No checks detected after 2 minutes - assuming no CI/CD is configured")
                        return {
                            'status': status,
                            'checks': checks,
                            'completed': True,
                            'no_checks_configured': True
                        }
                
                print()  # Add blank line for readability
                time.sleep(15)  # Wait 15 seconds before checking again
                
            except subprocess.CalledProcessError as e:
                print(f"⚠️  Error checking PR status: {e}")
                print("   Retrying in 15 seconds...")
                time.sleep(15)
                continue
        
        # Timeout reached
        print(f"⏰ Timeout reached after {timeout_seconds} seconds")
        return {
            'status': self.get_pr_status(pr_number, repo),
            'checks': self.get_pr_checks(pr_number, repo),
            'completed': False,
            'timeout': True
        }
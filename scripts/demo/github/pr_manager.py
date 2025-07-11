"""
Pull request management functionality for mutation testing PoC.
"""
import subprocess
import json
from pathlib import Path
from typing import Dict, Any, Optional
from .check_utils import CheckProcessor


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
                
                # Analyze individual checks first to determine completion
                checks_completed = False
                try:
                    if checks and isinstance(checks, list) and len(checks) > 0:
                        # Use the shared utility for consistent processing
                        CheckProcessor.print_check_summary(checks)
                        check_summary = CheckProcessor.get_check_summary(checks)
                        
                        # Check if all checks are completed (no running checks)
                        if check_summary['running_checks'] == 0 and check_summary['completed_checks'] == check_summary['total_checks']:
                            checks_completed = True
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
                except Exception as e:
                    import traceback
                    print(f"ERROR: Exception in individual checks analysis: {e}")
                    traceback.print_exc()
                
                # Analyze rollup status
                try:
                    if status.get('statusCheckRollup'):
                        rollup = status['statusCheckRollup']
                        
                        # Handle case where rollup is a dict
                        if isinstance(rollup, dict):
                            rollup_state = rollup.get('state', 'UNKNOWN')
                            print(f"📊 Overall status: {rollup_state}")
                            
                            if rollup.get('state') in ['SUCCESS', 'FAILURE', 'ERROR']:
                                print(f"✅ All checks completed with status: {rollup_state}")
                                return {
                                    'status': status,
                                    'checks': checks,
                                    'completed': True
                                }
                        # Handle case where rollup is a list (unexpected but happens)
                        elif isinstance(rollup, list):
                            if len(rollup) > 0 and isinstance(rollup[0], dict):
                                rollup_state = rollup[0].get('state', 'UNKNOWN')
                                print(f"📊 Overall status: {rollup_state} (from rollup list)")
                                
                                if rollup[0].get('state') in ['SUCCESS', 'FAILURE', 'ERROR']:
                                    print(f"✅ All checks completed with status: {rollup_state}")
                                    return {
                                        'status': status,
                                        'checks': checks,
                                        'completed': True
                                    }
                            else:
                                print("📊 Overall status: PENDING (rollup list is empty or invalid)")
                        else:
                            print(f"📊 Overall status: UNKNOWN (unexpected rollup type: {type(rollup)})")
                    else:
                        print("📊 Overall status: PENDING (no rollup data yet)")
                except Exception as e:
                    import traceback
                    print(f"ERROR: Exception in rollup status analysis: {e}")
                    traceback.print_exc()
                
                # If all individual checks are completed, exit even if rollup status is unclear
                if checks_completed:
                    print("✅ All individual checks completed - exiting wait loop")
                    return {
                        'status': status,
                        'checks': checks,
                        'completed': True
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
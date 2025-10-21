"""
Shared utilities for processing GitHub check results.
"""
import subprocess
import re
from pathlib import Path
from typing import Dict, Any, List, Optional

from temporal.github import artifact_utils
from temporal.github.artifact_utils import ArtifactDownload


class CheckProcessor:
    """Centralized logic for processing GitHub check results."""
    
    # Define the check status values
    STATUS_PASS = "pass"
    STATUS_FAIL = "fail"
    STATUS_PENDING = "pending"
    STATUS_SKIPPING = "skipping"
    STATUS_CANCEL = "cancel"
    
    # Completed statuses (not running anymore)
    COMPLETED_STATUSES = {STATUS_PASS, STATUS_FAIL, STATUS_CANCEL, STATUS_SKIPPING}
    
    # Running statuses 
    RUNNING_STATUSES = {STATUS_PENDING}
    
    @staticmethod
    def normalize_check(check: Dict[str, Any]) -> Dict[str, Any]:
        """Normalize a check result to a consistent format."""
        if not isinstance(check, dict):
            return {}
        
        return {
            'name': check.get('name', 'Unknown'),
            'state': check.get('state', 'unknown'),
            'bucket': check.get('bucket', 'unknown'),
            'url': check.get('link', ''),
            'started_at': check.get('startedAt'),
            'completed_at': check.get('completedAt'),
            'description': check.get('description', ''),
            'workflow': check.get('workflow', '')
        }
    
    @staticmethod
    def get_check_summary(checks: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Get a summary of check results."""
        if not checks:
            return {
                'total_checks': 0,
                'completed_checks': 0,
                'running_checks': 0,
                'passed_checks': 0,
                'failed_checks': 0,
                'cancelled_checks': 0,
                'skipped_checks': 0
            }
        
        # Normalize all checks first
        normalized_checks = [
            CheckProcessor.normalize_check(check) for check in checks
        ]
        
        total_checks = len(normalized_checks)
        passed_checks = sum(
            1
            for check in normalized_checks
            if check.get('bucket') == CheckProcessor.STATUS_PASS
        )
        failed_checks = sum(
            1
            for check in normalized_checks
            if check.get('bucket') == CheckProcessor.STATUS_FAIL
        )
        cancelled_checks = sum(
            1
            for check in normalized_checks
            if check.get('bucket') == CheckProcessor.STATUS_CANCEL
        )
        skipped_checks = sum(
            1
            for check in normalized_checks
            if check.get('bucket') == CheckProcessor.STATUS_SKIPPING
        )
        running_checks = sum(
            1
            for check in normalized_checks
            if check.get('bucket') == CheckProcessor.STATUS_PENDING
        )
        completed_checks = sum(
            1
            for check in normalized_checks
            if check.get('bucket') in CheckProcessor.COMPLETED_STATUSES
        )
        
        return {
            'total_checks': total_checks,
            'completed_checks': completed_checks,
            'running_checks': running_checks,
            'passed_checks': passed_checks,
            'failed_checks': failed_checks,
            'cancelled_checks': cancelled_checks,
            'skipped_checks': skipped_checks
        }
    
    @staticmethod
    def is_test_check(check: Dict[str, Any]) -> bool:
        """Determine if a check is a test-related check."""
        if not isinstance(check, dict):
            return False
        
        # Check both the check name and workflow name for test-related keywords
        test_keywords = ['test', 'pytest', 'unittest', 'ci', 'build']
        check_name = check.get('name', '').lower()
        workflow_name = check.get('workflow', '').lower()
        
        # Check if any keyword is in the check name or workflow name
        if any(keyword in check_name for keyword in test_keywords):
            return True
        if any(keyword in workflow_name for keyword in test_keywords):
            return True
        
        # Also check for Python version patterns that are typically test jobs
        # e.g., "3.8", "3.9", "3.10", "3.11", "3.12", "pypy3"
        python_version_pattern = r'^\d+\.\d+$|^pypy\d*$'
        import re
        if re.match(python_version_pattern, check_name):
            return True
        
        return False
    
    @staticmethod
    def get_failed_test_checks(
        checks: List[Dict[str, Any]],
        repo_path: str = None,
        repo: str = None,
    ) -> List[Dict[str, Any]]:
        """Get all failed test checks with detailed failure information."""
        failed_tests = []
        
        for check in checks:
            normalized_check = CheckProcessor.normalize_check(check)
            is_failed = normalized_check.get('bucket') == CheckProcessor.STATUS_FAIL
            if is_failed and CheckProcessor.is_test_check(normalized_check):
                
                # Get basic check info
                basic_info = {
                    'check_name': normalized_check.get('name'),
                    'details': normalized_check.get('description', 'No details available')
                }
                
                # If repo_path is provided, try to get detailed failure info
                if repo_path:
                    try:
                        detailed_info = CheckProcessor.get_failed_check_details(
                            normalized_check,
                            repo_path,
                            repo,
                        )
                        basic_info.update(detailed_info)
                    except Exception:
                        # If detailed extraction fails, keep basic info
                        basic_info['failure_reason'] = (
                            'due to unknown reasons (failed to fetch logs)'
                        )
                
                failed_tests.append(basic_info)
        
        return failed_tests
    
    @staticmethod
    def print_check_summary(checks: List[Dict[str, Any]]) -> None:
        """Print a formatted summary of check results."""
        if not checks:
            print("🔍 No checks available yet - GitHub Actions may still be starting up")
            return
        
        summary = CheckProcessor.get_check_summary(checks)
        
        print(
            "🔍 Checks summary: "
            f"{summary['total_checks']} total, "
            f"{summary['completed_checks']} completed, "
            f"{summary['running_checks']} running"
        )
        print(
            "   ✅ Passed: "
            f"{summary['passed_checks']}, "
            f"❌ Failed: {summary['failed_checks']}"
        )
        
        # Show individual check details (limit to first 10 to avoid spam)
        normalized_checks = [CheckProcessor.normalize_check(check) for check in checks]
        checks_to_show = normalized_checks[:10]
        
        for check in checks_to_show:
            check_name = check.get('name', 'Unknown')
            check_state = check.get('state', 'unknown')
            check_bucket = check.get('bucket', '')
            if check_bucket:
                print(f"   • {check_name}: {check_state} ({check_bucket})")
            else:
                print(f"   • {check_name}: {check_state}")
        
        if len(normalized_checks) > 10:
            print(f"   ... and {len(normalized_checks) - 10} more checks")
    
    @staticmethod
    def extract_run_id_from_url(check_url: str) -> Optional[str]:
        """Extract GitHub Actions run ID from check URL."""
        if not check_url:
            return None
        
        # GitHub Actions URLs typically look like:
        # https://github.com/owner/repo/actions/runs/12345678/job/98765432
        # https://github.com/owner/repo/runs/12345678
        match = re.search(r'/runs/(\d+)', check_url)
        if match:
            return match.group(1)
        return None

    @staticmethod
    def get_check_run_id(check: Dict[str, Any]) -> Optional[str]:
        """Resolve the workflow run identifier associated with a check."""
        if not isinstance(check, dict):
            return None
        check_url = check.get('url') or check.get('link')
        if not check_url:
            normalized = CheckProcessor.normalize_check(check)
            check_url = normalized.get('url')
        return CheckProcessor.extract_run_id_from_url(check_url or "")

    @staticmethod
    def list_check_artifacts(
        check: Dict[str, Any],
        repo_path: Optional[str] = None,
        repo: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """
        Return workflow artifacts tied to a check's run, if a repo path is known.
        """
        run_id = CheckProcessor.get_check_run_id(check)
        if not run_id or not repo_path:
            return []
        return artifact_utils.list_run_artifacts(
            run_id,
            Path(repo_path),
            repo=repo,
        )

    @staticmethod
    def download_check_junit_artifacts(
        check: Dict[str, Any],
        repo_path: Optional[str] = None,
        repo: Optional[str] = None,
        base_temp_dir: Optional[Path] = None,
    ) -> List[ArtifactDownload]:
        """
        Download artifacts for the given check that contain junit XML files.
        """
        run_id = CheckProcessor.get_check_run_id(check)
        if not run_id or not repo_path:
            return []
        return artifact_utils.download_all_junit_artifacts(
            run_id=run_id,
            repo_path=Path(repo_path),
            repo=repo,
            base_temp_dir=base_temp_dir,
        )
    
    @staticmethod
    def get_failed_check_details(
        check: Dict[str, Any],
        repo_path: str,
        repo: str = None,
    ) -> Dict[str, Any]:
        """Get detailed failure information for a failed check."""
        check_details = {
            'check_name': check.get('name', 'Unknown'),
            'failure_reason': 'due to reasons other than test case failure',
            'failed_tests': [],
            'log_available': False
        }
        
        # Extract run ID from the check URL
        check_url = check.get('url', check.get('link', ''))
        run_id = CheckProcessor.extract_run_id_from_url(check_url)
        
        if not run_id:
            check_details['failure_reason'] = (
                "due to unknown reasons "
                f"(no run ID found in URL: {check_url})"
            )
            return check_details
        
        try:
            # Get the failed logs for this run
            cmd = ["gh", "run", "view", run_id, "--log-failed"]
            if repo:
                cmd.extend(["--repo", repo])

            result = subprocess.run(
                cmd,
                cwd=repo_path,
                capture_output=True,
                text=True,
                timeout=30,
            )
            
            if result.returncode == 0:
                check_details['log_available'] = True
                log_output = result.stdout
                
                # Parse the log output to extract test failures
                failed_tests = CheckProcessor.parse_test_failures_from_log(
                    log_output
                )
                if failed_tests:
                    check_details['failed_tests'] = failed_tests
                    check_details['failure_reason'] = (
                        f"due to {len(failed_tests)} failed test case(s)"
                    )
                else:
                    # Look for other common failure patterns
                    if "error" in log_output.lower() or "failed" in log_output.lower():
                        check_details['failure_reason'] = (
                            "due to build or runtime errors"
                        )
            else:
                # If command failed, add debug info (truncate stderr to avoid too much output)
                stderr_msg = (
                    result.stderr[:200] + "..."
                    if len(result.stderr) > 200
                    else result.stderr
                )
                check_details['failure_reason'] = (
                    "due to unknown reasons "
                    f"(failed to fetch logs: {stderr_msg})"
                )
                    
        except (subprocess.TimeoutExpired, subprocess.CalledProcessError) as e:
            # If we can't get the logs, just return the basic info
            check_details['failure_reason'] = (
                "due to unknown reasons "
                f"(error: {str(e)[:200]})"
            )
        
        return check_details
    
    @staticmethod
    def parse_test_failures_from_log(log_output: str) -> List[str]:
        """Parse test failure information from log output."""
        failed_tests = []
        
        # Look for pytest short test summary info block (most reliable)
        summary_match = re.search(
            r'=+ short test summary info =+\s*\n(.*?)\n=+.*?=+', 
            log_output, 
            re.DOTALL | re.IGNORECASE
        )
        
        if summary_match:
            summary_block = summary_match.group(1)
            # Extract FAILED lines from the summary - be more specific
            failed_lines = re.findall(r'FAILED\s+([^\n\r]+)', summary_block)
            for line in failed_lines:
                line = line.strip()
                # Only include lines that look like proper test paths
                if line and '::' in line and line not in failed_tests:
                    # Filter out obvious noise patterns
                    if not re.match(r'^[\[\]:()]+$', line) and len(line) > 5:
                        failed_tests.append(line)
        
        # If no short summary found, look for individual FAILED patterns (fallback)
        if not failed_tests:
            # Only look for well-formed test paths
            pattern = (
                r'FAILED\s+((?:tests?/)?[a-zA-Z0-9_/.-]+\.py::[a-zA-Z0-9_]+'
                r'(?:\s+-\s+[^\n\r]+)?)'
            )
            matches = re.findall(
                pattern,
                log_output,
                re.IGNORECASE | re.MULTILINE,
            )
            for match in matches:
                test_info = match.strip()
                if test_info and test_info not in failed_tests:
                    failed_tests.append(test_info)
        
        return failed_tests[:10]  # Limit to first 10 failures to avoid overwhelming output

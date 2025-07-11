"""
Shared utilities for processing GitHub check results.
"""
from typing import Dict, Any, List


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
        normalized_checks = [CheckProcessor.normalize_check(check) for check in checks]
        
        total_checks = len(normalized_checks)
        passed_checks = sum(1 for check in normalized_checks if check.get('bucket') == CheckProcessor.STATUS_PASS)
        failed_checks = sum(1 for check in normalized_checks if check.get('bucket') == CheckProcessor.STATUS_FAIL)
        cancelled_checks = sum(1 for check in normalized_checks if check.get('bucket') == CheckProcessor.STATUS_CANCEL)
        skipped_checks = sum(1 for check in normalized_checks if check.get('bucket') == CheckProcessor.STATUS_SKIPPING)
        running_checks = sum(1 for check in normalized_checks if check.get('bucket') == CheckProcessor.STATUS_PENDING)
        completed_checks = sum(1 for check in normalized_checks if check.get('bucket') in CheckProcessor.COMPLETED_STATUSES)
        
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
        test_keywords = ['test', 'pytest', 'unittest', 'ci', 'build']
        check_name = check.get('name', '').lower()
        return any(keyword in check_name for keyword in test_keywords)
    
    @staticmethod
    def get_failed_test_checks(checks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Get all failed test checks."""
        failed_tests = []
        
        for check in checks:
            normalized_check = CheckProcessor.normalize_check(check)
            if (normalized_check.get('bucket') == CheckProcessor.STATUS_FAIL and 
                CheckProcessor.is_test_check(normalized_check)):
                failed_tests.append({
                    'check_name': normalized_check.get('name'),
                    'details': normalized_check.get('description', 'No details available')
                })
        
        return failed_tests
    
    @staticmethod
    def print_check_summary(checks: List[Dict[str, Any]]) -> None:
        """Print a formatted summary of check results."""
        if not checks:
            print("🔍 No checks available yet - GitHub Actions may still be starting up")
            return
        
        summary = CheckProcessor.get_check_summary(checks)
        
        print(f"🔍 Checks summary: {summary['total_checks']} total, {summary['completed_checks']} completed, {summary['running_checks']} running")
        print(f"   ✅ Passed: {summary['passed_checks']}, ❌ Failed: {summary['failed_checks']}")
        
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
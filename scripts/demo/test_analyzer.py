"""
Test result analysis functionality for mutation testing PoC.
"""
import json
from pathlib import Path
from typing import Dict, Any, List
from datetime import datetime


class TestAnalyzer:
    def __init__(self, output_dir: Path = None):
        self.output_dir = output_dir or Path("./test_results")
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def analyze_pr_results(self, pr_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze PR check results and extract test information."""
        analysis = {
            'pr_number': pr_data.get('status', {}).get('number'),
            'pr_url': pr_data.get('status', {}).get('url'),
            'timestamp': datetime.now().isoformat(),
            'completed': pr_data.get('completed', False),
            'timeout': pr_data.get('timeout', False),
            'overall_status': None,
            'checks': [],
            'test_failures': [],
            'summary': {}
        }
        
        # Extract overall status
        status = pr_data.get('status', {})
        if status.get('statusCheckRollup'):
            analysis['overall_status'] = status['statusCheckRollup'].get('state')
        
        # Process individual checks
        checks = pr_data.get('checks', [])
        
        try:
            for check in checks:
                if isinstance(check, dict):
                    check_info = {
                        'name': check.get('name'),
                        'status': check.get('status'),
                        'conclusion': check.get('conclusion'),
                        'url': check.get('url'),
                        'started_at': check.get('started_at'),
                        'completed_at': check.get('completed_at')
                    }
                    analysis['checks'].append(check_info)
                    
                    # Extract test failures if this is a test check
                    if check.get('conclusion') == 'failure' and self._is_test_check(check):
                        analysis['test_failures'].append({
                            'check_name': check.get('name'),
                            'details': check.get('details', 'No details available')
                        })
        except Exception as e:
            import traceback
            print(f"ERROR: Exception in checks processing: {e}")
            traceback.print_exc()
        
        # Generate summary
        analysis['summary'] = self._generate_summary(analysis)
        
        return analysis
    
    def _is_test_check(self, check: Dict[str, Any]) -> bool:
        """Determine if a check is a test-related check."""
        if not isinstance(check, dict):
            return False
        test_keywords = ['test', 'pytest', 'unittest', 'ci', 'build']
        check_name = check.get('name', '').lower()
        return any(keyword in check_name for keyword in test_keywords)
    
    def _generate_summary(self, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Generate a summary of the test results."""
        total_checks = len(analysis['checks'])
        failed_checks = len([c for c in analysis['checks'] if c.get('conclusion') == 'failure'])
        passed_checks = len([c for c in analysis['checks'] if c.get('conclusion') == 'success'])
        
        return {
            'total_checks': total_checks,
            'passed_checks': passed_checks,
            'failed_checks': failed_checks,
            'test_failures_count': len(analysis['test_failures']),
            'mutation_killed': failed_checks > 0,  # If any tests fail, mutation is "killed"
            'mutation_survived': failed_checks == 0 and analysis['completed']
        }
    
    def save_results(self, analysis: Dict[str, Any], filename: str = None) -> Path:
        """Save analysis results to a JSON file."""
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            pr_number = analysis.get('pr_number', 'unknown')
            filename = f"test_results_pr_{pr_number}_{timestamp}.json"
        
        output_path = self.output_dir / filename
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(analysis, f, indent=2, ensure_ascii=False)
        
        return output_path
    
    def load_results(self, filepath: Path) -> Dict[str, Any]:
        """Load analysis results from a JSON file."""
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
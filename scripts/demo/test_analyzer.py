"""
Test result analysis functionality for mutation testing PoC.
"""
import json
from pathlib import Path
from typing import Dict, Any
from datetime import datetime
from check_utils import CheckProcessor


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
            rollup = status['statusCheckRollup']
            # Handle case where rollup is a dict
            if isinstance(rollup, dict):
                analysis['overall_status'] = rollup.get('state')
            # Handle case where rollup is a list (unexpected but happens)
            elif isinstance(rollup, list) and len(rollup) > 0 and isinstance(rollup[0], dict):
                analysis['overall_status'] = rollup[0].get('state')
            else:
                analysis['overall_status'] = 'UNKNOWN'
        
        # Process individual checks
        checks = pr_data.get('checks', [])
        
        try:
            # Normalize all checks using the shared utility
            for check in checks:
                normalized_check = CheckProcessor.normalize_check(check)
                analysis['checks'].append(normalized_check)
            
            # Extract test failures using the shared utility
            analysis['test_failures'] = CheckProcessor.get_failed_test_checks(checks)
            
        except Exception as e:
            import traceback
            print(f"ERROR: Exception in checks processing: {e}")
            traceback.print_exc()
        
        # Generate summary
        analysis['summary'] = self._generate_summary(analysis)
        
        return analysis
    
    def _generate_summary(self, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Generate a summary of the test results."""
        # Use the shared utility to get consistent summary
        check_summary = CheckProcessor.get_check_summary(analysis['checks'])
        
        return {
            'total_checks': check_summary['total_checks'],
            'passed_checks': check_summary['passed_checks'],
            'failed_checks': check_summary['failed_checks'],
            'test_failures_count': len(analysis['test_failures']),
            'mutation_killed': check_summary['failed_checks'] > 0,  # If any tests fail, mutation is "killed"
            'mutation_survived': check_summary['failed_checks'] == 0 and analysis['completed']
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
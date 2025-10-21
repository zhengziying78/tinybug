"""
Test result analysis functionality for mutation testing PoC.
"""
import json
import tempfile
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional
from xml.etree import ElementTree

from temporal.github.check_utils import CheckProcessor


class TestAnalyzer:
    def __init__(self, output_dir: Optional[Path] = None, repo_path: Optional[Path] = None):
        self.output_dir = output_dir or Path.home() / "Desktop"
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.repo_path = repo_path
    
    def analyze_pr_results(self, pr_data: Dict[str, Any], repo: str = None) -> Dict[str, Any]:
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
            
            repo_path_str = str(self.repo_path) if self.repo_path else None
            analysis['test_failures'] = self._analyze_failed_checks(
                checks=checks,
                repo_path=repo_path_str,
                repo=repo,
            )
            
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
            # If any tests fail, the mutation is considered "killed".
            'mutation_killed': check_summary['failed_checks'] > 0,
            'mutation_survived': (
                check_summary['failed_checks'] == 0 and analysis['completed']
            )
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

    def _analyze_failed_checks(
        self,
        checks: List[Dict[str, Any]],
        repo_path: Optional[str],
        repo: Optional[str],
    ) -> List[Dict[str, Any]]:
        """
        Inspect failed test checks and prefer junit artifacts over log scraping.
        """
        failures: List[Dict[str, Any]] = []
        for check in checks:
            normalized = CheckProcessor.normalize_check(check)
            if normalized.get('bucket') != CheckProcessor.STATUS_FAIL:
                continue
            if not CheckProcessor.is_test_check(normalized):
                continue

            failure_detail: Dict[str, Any] = {
                'check_name': normalized.get('name'),
                'details': normalized.get('description', 'No details available'),
            }

            artifact_detail = self._extract_test_results_from_artifacts(
                check=check,
                repo_path=repo_path,
                repo=repo,
            )
            if artifact_detail:
                failure_detail.update(artifact_detail)
            elif repo_path:
                try:
                    log_details = CheckProcessor.get_failed_check_details(
                        normalized,
                        repo_path,
                        repo,
                    )
                    failure_detail.update(log_details)
                except Exception:
                    failure_detail.setdefault(
                        'failure_reason',
                        'due to unknown reasons (failed to fetch logs)',
                    )

            failure_detail.setdefault('failed_tests', [])
            failure_detail.setdefault('failure_reason', 'due to unknown reasons')
            failures.append(failure_detail)
        return failures

    def _extract_test_results_from_artifacts(
        self,
        check: Dict[str, Any],
        repo_path: Optional[str],
        repo: Optional[str],
    ) -> Optional[Dict[str, Any]]:
        """
        Attempt to gather structured junit outcomes from workflow artifacts.
        """
        if not repo_path:
            return None

        with tempfile.TemporaryDirectory(prefix="test-analyzer-artifacts-") as temp_dir:
            try:
                downloads = CheckProcessor.download_check_junit_artifacts(
                    check,
                    repo_path=repo_path,
                    repo=repo,
                    base_temp_dir=Path(temp_dir),
                )
            except Exception:
                return None

            if not downloads:
                return None

            all_tests: List[Dict[str, Any]] = []
            artifact_sources: List[Dict[str, Any]] = []

            for download in downloads:
                artifact_sources.append(
                    {
                        'artifact': download.name,
                        'files': [path.name for path in download.junit_paths],
                    }
                )
                for junit_path in download.junit_paths:
                    all_tests.extend(
                        self._parse_junit_file(junit_path, artifact_name=download.name)
                    )

            if not all_tests:
                return None

            tests_summary = self._summarize_tests(all_tests)
            failing_tests = [
                test['id']
                for test in all_tests
                if test['status'] in {'failed', 'error'}
            ]

            failure_reason = (
                f"due to {len(failing_tests)} failed test case(s)"
                if failing_tests
                else "due to test results reported in junit artifacts"
            )

            return {
                'failure_reason': failure_reason,
                'failed_tests': failing_tests,
                'tests': all_tests,
                'tests_summary': tests_summary,
                'junit_artifacts': artifact_sources,
                'log_available': False,
            }

    def _parse_junit_file(
        self,
        junit_path: Path,
        *,
        artifact_name: str,
    ) -> List[Dict[str, Any]]:
        """Return per-test outcomes from a junit XML document."""
        try:
            tree = ElementTree.parse(junit_path)
        except (ElementTree.ParseError, OSError):
            return []

        root = tree.getroot()
        tests: List[Dict[str, Any]] = []
        for testcase in root.iter():
            if self._strip_xml_namespace(testcase.tag) != "testcase":
                continue

            name = testcase.get('name') or 'unknown'
            classname = testcase.get('classname') or ''
            duration = testcase.get('time')

            status = 'passed'
            message: Optional[str] = None
            output: Optional[str] = None

            for child in list(testcase):
                tag = self._strip_xml_namespace(child.tag)
                child_text = (child.text or '').strip() or None
                child_message = child.get('message') or child_text
                if tag == 'failure':
                    status = 'failed'
                    message = child_message
                    output = child_text
                    break
                if tag == 'error':
                    status = 'error'
                    message = child_message
                    output = child_text
                    break
                if tag == 'skipped':
                    status = 'skipped'
                    message = child_message
                    output = child_text
                    break

            tests.append(
                {
                    'id': self._format_test_identifier(classname, name),
                    'name': name,
                    'classname': classname,
                    'status': status,
                    'message': message,
                    'output': output,
                    'duration': duration,
                    'source_artifact': artifact_name,
                    'source_file': junit_path.name,
                }
            )
        return tests

    @staticmethod
    def _strip_xml_namespace(tag: str) -> str:
        """Remove XML namespace from a tag name if present."""
        if '}' in tag:
            return tag.split('}', 1)[1]
        return tag

    @staticmethod
    def _format_test_identifier(classname: str, name: str) -> str:
        """Format test identifiers consistently for summaries."""
        if classname:
            return f"{classname}::{name}"
        return name

    @staticmethod
    def _summarize_tests(tests: List[Dict[str, Any]]) -> Dict[str, int]:
        """Return aggregate counts for junit test outcomes."""
        summary = {
            'total': len(tests),
            'passed': 0,
            'failed': 0,
            'errors': 0,
            'skipped': 0,
        }
        for test in tests:
            status = test.get('status')
            if status == 'passed':
                summary['passed'] += 1
            elif status == 'failed':
                summary['failed'] += 1
            elif status == 'error':
                summary['errors'] += 1
            elif status == 'skipped':
                summary['skipped'] += 1
        return summary

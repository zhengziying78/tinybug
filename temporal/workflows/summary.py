"""
Utilities for rendering mutation workflow summaries.
"""
from __future__ import annotations

from typing import Any, List, Mapping

from temporal.workflows.mutation_flow import MutationFlowResult


def render_summary_lines(
    repo_config: Mapping[str, Any],
    flow_result: MutationFlowResult,
) -> List[str]:
    """Return formatted summary lines for a mutation workflow result."""
    lines: List[str] = []
    lines.append("Mutation testing summary:")
    lines.append(f"  - Repository: {repo_config['url']}")
    lines.append(f"  - Branch: {flow_result.context.branch_name}")
    lines.append(f"  - Pull request: {flow_result.outcome.pr_url or 'N/A'}")
    lines.append(f"  - Mutation applied: {flow_result.outcome.mutation_applied}")

    if flow_result.outcome.analysis:
        summary = flow_result.outcome.analysis.get("summary", {})
        lines.append(f"  - Total checks: {summary.get('total_checks', 0)}")
        lines.append(f"  - Passed checks: {summary.get('passed_checks', 0)}")
        lines.append(f"  - Failed checks: {summary.get('failed_checks', 0)}")
        lines.append(f"  - Mutation killed: {summary.get('mutation_killed', False)}")
        lines.append(f"  - Mutation survived: {summary.get('mutation_survived', False)}")
        lines.append(f"  - Results file: {flow_result.outcome.results_file}")

        if flow_result.outcome.summary_file:
            lines.append(f"  - Summary file: {flow_result.outcome.summary_file}")

        failures = flow_result.outcome.analysis.get("test_failures") or []
        if failures:
            lines.append("")
            lines.append("Detailed failure information:")
            for failure in failures:
                check_name = failure.get("check_name", "Unknown")
                failure_reason = failure.get("failure_reason", "due to unknown reasons")
                lines.append(f"  • {check_name}: {failure_reason}")
                failed_tests = failure.get("failed_tests") or []
                if failed_tests:
                    lines.append("    Failed tests:")
                    for test in failed_tests:
                        lines.append(f"      - {test}")
            lines.append("")
    else:
        lines.append("  - No analysis available")
        if flow_result.outcome.summary_file:
            lines.append(f"  - Summary file: {flow_result.outcome.summary_file}")

    if flow_result.outcome.error:
        lines.append("")
        lines.append("Errors encountered during workflow:")
        lines.append(f"  - {flow_result.outcome.error}")
        if flow_result.outcome.traceback:
            lines.append(flow_result.outcome.traceback)

    lines.append("")
    lines.append(f"Cleanup results: {flow_result.workflow.cleanup_details}")
    return lines

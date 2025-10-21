from __future__ import annotations

from pathlib import Path
from unittest import mock

from temporal.github.artifact_utils import ArtifactDownload
from temporal.github.check_utils import CheckProcessor
from temporal.github.test_analyzer import TestAnalyzer


FIXTURES_DIR = Path(__file__).resolve().parent / "fixtures"
JUNIT_FIXTURE = FIXTURES_DIR / "pytest_sample_junit.xml"


def _build_pr_data(check: dict) -> dict:
    return {
        "status": {
            "number": 42,
            "url": "https://github.com/org/repo/pull/42",
            "statusCheckRollup": {"state": "FAILURE"},
        },
        "checks": [check],
        "completed": True,
        "timeout": False,
    }


def _build_failed_check() -> dict:
    return {
        "name": "pytest (3.11)",
        "state": "COMPLETED",
        "bucket": CheckProcessor.STATUS_FAIL,
        "link": "https://github.com/org/repo/actions/runs/123456",
        "description": "1 failing test",
        "workflow": "Tests",
    }


def test_analyzer_prefers_junit_artifacts(tmp_path: Path) -> None:
    analyzer = TestAnalyzer(repo_path=tmp_path)
    pr_data = _build_pr_data(_build_failed_check())

    archive_path = tmp_path / "pytest-junit.zip"
    archive_path.write_bytes(b"")
    download = ArtifactDownload(
        name="pytest-junit",
        archive_path=archive_path,
        extract_path=tmp_path,
        junit_paths=[JUNIT_FIXTURE],
    )

    with mock.patch.object(
        CheckProcessor,
        "download_check_junit_artifacts",
        return_value=[download],
    ) as download_mock, mock.patch.object(
        CheckProcessor,
        "get_failed_check_details",
    ) as log_mock:
        analysis = analyzer.analyze_pr_results(pr_data, repo="org/repo")

    download_mock.assert_called_once()
    log_mock.assert_not_called()

    failures = analysis["test_failures"]
    assert len(failures) == 1
    failure = failures[0]

    assert failure["failure_reason"] == "due to 1 failed test case(s)"
    assert failure["failed_tests"] == ["tests.test_example::test_fail"]
    assert failure["tests_summary"] == {
        "total": 2,
        "passed": 1,
        "failed": 1,
        "errors": 0,
        "skipped": 0,
    }
    assert failure["log_available"] is False
    assert failure["junit_artifacts"] == [
        {"artifact": "pytest-junit", "files": [JUNIT_FIXTURE.name]}
    ]


def test_analyzer_falls_back_to_logs_when_no_artifacts(tmp_path: Path) -> None:
    analyzer = TestAnalyzer(repo_path=tmp_path)
    pr_data = _build_pr_data(_build_failed_check())

    log_details = {
        "failure_reason": "due to log scraping",
        "failed_tests": ["tests.test_example::test_fail"],
        "log_available": True,
    }

    with mock.patch.object(
        CheckProcessor,
        "download_check_junit_artifacts",
        return_value=[],
    ) as download_mock, mock.patch.object(
        CheckProcessor,
        "get_failed_check_details",
        return_value=log_details,
    ) as log_mock:
        analysis = analyzer.analyze_pr_results(pr_data)

    download_mock.assert_called_once()
    log_mock.assert_called_once()

    failures = analysis["test_failures"]
    assert len(failures) == 1
    failure = failures[0]
    assert failure["failure_reason"] == log_details["failure_reason"]
    assert failure["failed_tests"] == log_details["failed_tests"]
    assert failure["log_available"] is True


def test_analyzer_uses_log_fallback_on_invalid_artifacts(tmp_path: Path) -> None:
    analyzer = TestAnalyzer(repo_path=tmp_path)
    pr_data = _build_pr_data(_build_failed_check())

    archive_path = tmp_path / "pytest-junit.zip"
    archive_path.write_bytes(b"")
    download = ArtifactDownload(
        name="pytest-junit",
        archive_path=archive_path,
        extract_path=tmp_path,
        junit_paths=[tmp_path / "missing.xml"],
    )

    log_details = {
        "failure_reason": "due to unknown reasons (failed to fetch logs)",
        "failed_tests": ["legacy::from_logs"],
        "log_available": True,
    }

    with mock.patch.object(
        CheckProcessor,
        "download_check_junit_artifacts",
        return_value=[download],
    ) as download_mock, mock.patch.object(
        TestAnalyzer,
        "_parse_junit_file",
        return_value=[],
    ) as parse_mock, mock.patch.object(
        CheckProcessor,
        "get_failed_check_details",
        return_value=log_details,
    ) as log_mock:
        analysis = analyzer.analyze_pr_results(pr_data)

    download_mock.assert_called_once()
    parse_mock.assert_called()
    log_mock.assert_called_once()

    failures = analysis["test_failures"]
    assert len(failures) == 1
    failure = failures[0]
    assert failure["failed_tests"] == log_details["failed_tests"]
    assert failure["log_available"] is True

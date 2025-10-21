from __future__ import annotations

import os
import time
from pathlib import Path

from temporal.github import artifact_utils


FIXTURES_DIR = Path(__file__).resolve().parent / "fixtures"
JUNIT_FIXTURE = FIXTURES_DIR / "pytest_sample_junit.xml"


def test_discover_junit_reports_identifies_fixture(tmp_path: Path) -> None:
    target_dir = tmp_path / "results"
    target_dir.mkdir()
    destination = target_dir / "report.xml"
    destination.write_text(JUNIT_FIXTURE.read_text(encoding="utf-8"), encoding="utf-8")

    discovered = list(artifact_utils._discover_junit_reports(target_dir))
    assert destination in discovered


def test_resolve_archive_path_prefers_named_zip(tmp_path: Path) -> None:
    archive_dir = tmp_path / "archives"
    archive_dir.mkdir()
    explicit = archive_dir / "pytest-junit.zip"
    explicit.write_bytes(b"")
    alt = archive_dir / "fallback.zip"
    alt.write_bytes(b"")

    resolved = artifact_utils._resolve_archive_path(archive_dir, "pytest-junit")
    assert resolved == explicit


def test_resolve_archive_path_falls_back_to_latest_zip(tmp_path: Path) -> None:
    archive_dir = tmp_path / "archives"
    archive_dir.mkdir()

    older = archive_dir / "older.zip"
    older.write_bytes(b"")
    newer = archive_dir / "newer.zip"
    newer.write_bytes(b"")

    # Ensure mtimes differ so the helper selects the most recent archive
    time.sleep(0.01)
    os.utime(newer, None)

    resolved = artifact_utils._resolve_archive_path(archive_dir, "missing-name")
    assert resolved == newer

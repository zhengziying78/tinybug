"""
Helpers for interacting with GitHub Actions workflow artifacts via the gh CLI.
"""
from __future__ import annotations

import json
import subprocess
import tempfile
import zipfile
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Sequence


GH_TIMEOUT_SECONDS = 60


@dataclass
class ArtifactDownload:
    """Materialized artifact contents plus discovered junit report paths."""

    name: str
    archive_path: Path
    extract_path: Path
    junit_paths: List[Path]


def _gh_repo_args(repo: Optional[str]) -> List[str]:
    """Build reusable repo arguments for gh commands."""
    if repo:
        return ["--repo", repo]
    return []


def _run_gh_command(
    args: Sequence[str],
    repo_path: Path,
    timeout: int = GH_TIMEOUT_SECONDS,
) -> subprocess.CompletedProcess:
    """Execute a gh CLI command and surface stderr on failure."""
    result = subprocess.run(
        ["gh", *args],
        cwd=str(repo_path),
        capture_output=True,
        text=True,
        timeout=timeout,
    )
    if result.returncode != 0:
        stderr_preview = result.stderr.strip()
        raise RuntimeError(
            f"gh {' '.join(args)} failed: {stderr_preview or 'unknown error'}"
        )
    return result


def list_run_artifacts(
    run_id: str,
    repo_path: Path,
    repo: Optional[str] = None,
) -> List[Dict[str, Any]]:
    """
    Return available artifacts for the provided workflow run.

    Uses `gh run view --json artifacts` to avoid introducing a REST dependency.
    """
    args: List[str] = ["run", "view", run_id, "--json", "artifacts"]
    args.extend(_gh_repo_args(repo))
    result = _run_gh_command(args, repo_path)
    try:
        payload = json.loads(result.stdout or "{}")
    except json.JSONDecodeError as exc:
        raise RuntimeError(f"Unable to parse gh artifacts payload: {exc}") from exc

    artifacts = payload.get("artifacts")
    if isinstance(artifacts, list):
        return artifacts
    return []


def download_artifact_archive(
    run_id: str,
    artifact_name: str,
    repo_path: Path,
    repo: Optional[str] = None,
    base_temp_dir: Optional[Path] = None,
) -> ArtifactDownload:
    """
    Download and extract a workflow artifact archive into an isolated temp dir.
    """
    if base_temp_dir is None:
        base_temp_dir = Path(tempfile.mkdtemp(prefix="artifact-download-"))
    else:
        base_temp_dir.mkdir(parents=True, exist_ok=True)

    archive_dir = base_temp_dir / "archives"
    archive_dir.mkdir(parents=True, exist_ok=True)
    extract_root = base_temp_dir / "extracted"
    extract_root.mkdir(parents=True, exist_ok=True)

    download_args: List[str] = [
        "run",
        "download",
        run_id,
        "--name",
        artifact_name,
        "--archive",
        "zip",
        "--dir",
        str(archive_dir),
    ]
    download_args.extend(_gh_repo_args(repo))
    _run_gh_command(download_args, repo_path)

    archive_path = _resolve_archive_path(archive_dir, artifact_name)
    extract_path = Path(tempfile.mkdtemp(prefix=f"{artifact_name}-", dir=extract_root))

    with zipfile.ZipFile(archive_path, "r") as zip_file:
        zip_file.extractall(path=extract_path)

    junit_paths = list(_discover_junit_reports(extract_path))
    return ArtifactDownload(
        name=artifact_name,
        archive_path=archive_path,
        extract_path=extract_path,
        junit_paths=junit_paths,
    )


def download_all_junit_artifacts(
    run_id: str,
    repo_path: Path,
    repo: Optional[str] = None,
    base_temp_dir: Optional[Path] = None,
) -> List[ArtifactDownload]:
    """
    Download all artifacts for a run and return ones that contain junit reports.
    """
    artifacts = list_run_artifacts(run_id, repo_path, repo)
    junit_downloads: List[ArtifactDownload] = []
    for artifact in artifacts:
        name = artifact.get("name")
        if not name:
            continue
        try:
            download = download_artifact_archive(
                run_id=run_id,
                artifact_name=name,
                repo_path=repo_path,
                repo=repo,
                base_temp_dir=base_temp_dir,
            )
        except Exception:
            continue
        if download.junit_paths:
            junit_downloads.append(download)
    return junit_downloads


def _resolve_archive_path(archive_dir: Path, artifact_name: str) -> Path:
    """
    Determine the zip file gh produced for the downloaded artifact.
    """
    candidate = archive_dir / f"{artifact_name}.zip"
    if candidate.exists():
        return candidate
    zips = sorted(archive_dir.glob("*.zip"), key=lambda p: p.stat().st_mtime, reverse=True)
    if not zips:
        raise FileNotFoundError(
            f"No zip archive found after downloading artifact '{artifact_name}'"
        )
    return zips[0]


def _discover_junit_reports(root: Path) -> Iterable[Path]:
    """Search for junit XML reports within an extracted artifact directory."""
    if not root.exists():
        return
    for xml_path in root.rglob("*.xml"):
        try:
            with xml_path.open("r", encoding="utf-8") as handle:
                snippet = handle.read(256).lower()
        except (OSError, UnicodeDecodeError):
            continue
        if "<testsuite" in snippet or "<testsuites" in snippet:
            yield xml_path

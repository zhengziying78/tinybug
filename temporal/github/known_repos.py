"""
Repository definitions consumed by the mutation workflows and demo CLI.
"""
from __future__ import annotations

from typing import Any, Dict


# Repository configuration keyed by canonical repo name.
KNOWN_REPOS: Dict[str, Dict[str, Any]] = {
    "demo-httpie-cli": {
        "name": "demo-httpie-cli",
        "url": "https://github.com/zhengziying78/demo-httpie-cli",
        "base_branch": "master",
        "repo_id": "zhengziying78/demo-httpie-cli",
    },
    "demo-pallets-click": {
        "name": "demo-pallets-click",
        "url": "https://github.com/zhengziying78/demo-pallets-click",
        "base_branch": "main",
        "repo_id": "zhengziying78/demo-pallets-click",
    },
    "demo-psf-requests": {
        "name": "demo-psf-requests",
        "url": "https://github.com/zhengziying78/demo-psf-requests",
        "base_branch": "main",
        "repo_id": "zhengziying78/demo-psf-requests",
    },
}

# Default repo name (demo-httpie-cli).
DEFAULT_REPO_NAME = "demo-httpie-cli"


__all__ = ["KNOWN_REPOS", "DEFAULT_REPO_NAME"]

"""
Repository definitions consumed by the demo mutation flow.
"""
from __future__ import annotations

from typing import Any, Dict, Iterable, List, Tuple

from mutation.mutations import get_mutation

# Repository configuration keyed by canonical repo name.
KNOWN_REPOS: Dict[str, Dict[str, Any]] = {
    "demo-httpie-cli": {
        "name": "demo-httpie-cli",
        "url": "https://github.com/zhengziying78/demo-httpie-cli",
        "base_branch": "master",
        "repo_id": "zhengziying78/demo-httpie-cli",
        "mutation": get_mutation("demo-httpie-cli"),
    },
    "demo-pallets-click": {
        "name": "demo-pallets-click",
        "url": "https://github.com/zhengziying78/demo-pallets-click",
        "base_branch": "main",
        "repo_id": "zhengziying78/demo-pallets-click",
        "mutation": get_mutation("demo-pallets-click"),
    },
    "demo-psf-requests": {
        "name": "demo-psf-requests",
        "url": "https://github.com/zhengziying78/demo-psf-requests",
        "base_branch": "main",
        "repo_id": "zhengziying78/demo-psf-requests",
        "mutation": get_mutation("demo-psf-requests"),
    },
}

# Default repo name (demo-httpie-cli).
DEFAULT_REPO_NAME = "demo-httpie-cli"


def repo_menu_entries() -> List[Tuple[str, Dict[str, Any]]]:
    """
    Return repo entries as a list for menu display.

    The order matches the definition order above.
    """
    return list(KNOWN_REPOS.items())


def repo_choices() -> Iterable[str]:
    """Return available repo names."""
    return KNOWN_REPOS.keys()

"""
Mutation configurations consumed by the Temporal mutation workflow.
"""

from __future__ import annotations

from typing import Dict, List, Optional

# Mutation configurations for different repositories
MUTATIONS: Dict[str, List[Dict[str, object]]] = {
    "demo-httpie-cli": [
        {
            "id": "none_check_logic",
            "file_path": "httpie/cli/dicts.py",
            "line_number": 26,
            "find_pattern": r"if value is None:",
            "replace_pattern": "if value is not None:",
            "description": "Change None check logic",
        }
    ],
    "demo-pallets-click": [
        {
            "id": "encoding_assignment",
            "file_path": "src/click/utils.py",
            "line_number": 126,
            "find_pattern": r"self.encoding = encoding",
            "replace_pattern": 'self.encoding = "utf-16"',
            "description": "Change encoding assignment",
        }
    ],
    "demo-psf-requests": [
        {
            "id": "status_code_description",
            "file_path": "src/requests/status_codes.py",
            "line_number": 87,
            "find_pattern": r'444: \("no_response", "none"\),',
            "replace_pattern": '444: ("no_response", "no"),',
            "description": "Change status code description",
        }
    ],
}


def get_mutation(repo_name: str) -> Optional[Dict[str, object]]:
    """
    Get the default mutation configuration for a repository.

    Args:
        repo_name: Name of the repository.

    Returns:
        Mutation configuration dictionary, or None if not found.
    """
    mutations = MUTATIONS.get(repo_name)
    if not mutations:
        return None

    return mutations[0]

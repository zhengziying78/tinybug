"""
Mutation configurations consumed by the Temporal mutation workflow.
"""

from __future__ import annotations

import random
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
        },
        {
            "id": "none_check_always_true",
            "file_path": "httpie/cli/dicts.py",
            "line_number": 26,
            "find_pattern": r"if value is None:",
            "replace_pattern": "if True:",
            "description": "Force branch to always execute",
        },
        {
            "id": "none_check_always_false",
            "file_path": "httpie/cli/dicts.py",
            "line_number": 26,
            "find_pattern": r"if value is None:",
            "replace_pattern": "if False:",
            "description": "Prevent branch from ever executing",
        },
    ],
    "demo-pallets-click": [
        {
            "id": "encoding_assignment",
            "file_path": "src/click/utils.py",
            "line_number": 126,
            "find_pattern": r"self.encoding = encoding",
            "replace_pattern": 'self.encoding = "utf-16"',
            "description": "Change encoding assignment",
        },
        {
            "id": "encoding_none",
            "file_path": "src/click/utils.py",
            "line_number": 126,
            "find_pattern": r"self.encoding = encoding",
            "replace_pattern": "self.encoding = None",
            "description": "Remove configured encoding",
        },
        {
            "id": "encoding_ascii",
            "file_path": "src/click/utils.py",
            "line_number": 126,
            "find_pattern": r"self.encoding = encoding",
            "replace_pattern": 'self.encoding = "ascii"',
            "description": "Force ASCII encoding",
        },
    ],
    "demo-psf-requests": [
        {
            "id": "status_code_description",
            "file_path": "src/requests/status_codes.py",
            "line_number": 87,
            "find_pattern": r'444: \("no_response", "none"\),',
            "replace_pattern": '444: ("no_response", "no"),',
            "description": "Change status code description",
        },
        {
            "id": "status_code_timeout_description",
            "file_path": "src/requests/status_codes.py",
            "line_number": 87,
            "find_pattern": r'444: \("no_response", "none"\),',
            "replace_pattern": '444: ("no_response", "timeout"),',
            "description": "Change status code to timeout",
        },
        {
            "id": "status_code_empty_description",
            "file_path": "src/requests/status_codes.py",
            "line_number": 87,
            "find_pattern": r'444: \("no_response", "none"\),',
            "replace_pattern": '444: ("no_response", ""),',
            "description": "Remove status code description",
        },
    ],
}


def get_mutation(repo_name: str, mutation_id: Optional[str] = None) -> Dict[str, object]:
    """
    Get the mutation configuration for a repository.

    Args:
        repo_name: Name of the repository.
        mutation_id: Optional mutation identifier to select a specific mutation.

    Returns:
        Mutation configuration dictionary, or None if not found.
    """
    mutations = MUTATIONS.get(repo_name)
    if not mutations:
        available = ", ".join(sorted(MUTATIONS.keys()))
        raise ValueError(
            f"No mutations configured for repository '{repo_name}'. "
            f"Available repositories: {available or 'none'}"
        )

    if mutation_id is None:
        return random.choice(mutations)

    for mutation in mutations:
        if mutation.get("id") == mutation_id:
            return mutation

    available_mutations = ", ".join(m.get("id", "<unknown>") for m in mutations)
    raise ValueError(
        f"Unknown mutation '{mutation_id}' for repository '{repo_name}'. "
        f"Available mutations: {available_mutations or 'none'}"
    )

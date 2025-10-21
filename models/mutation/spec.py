"""
Data classes representing mutation specifications shared across services.
"""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class MutationSpec:
    """Concrete mutation parameters applied to a repository checkout."""

    file_path: str
    line_number: int
    find_pattern: str
    replace_pattern: str

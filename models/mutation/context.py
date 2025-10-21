"""Immutable context describing a mutation workflow run."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class MutationContext:
    """Static context describing the mutation run."""

    repo_url: str
    branch_name: str
    pr_title: str
    mutation_description: str
    pr_number: Optional[str] = None
    pr_url: Optional[str] = None
    repo_id: Optional[str] = None
    base_branch: Optional[str] = None
    timestamp: Optional[str] = None

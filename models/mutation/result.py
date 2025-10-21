"""Outcome data captured from mutation workflow executions."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Optional


@dataclass
class MutationResult:
    """Outcome of executing the mutation run."""

    pr_number: Optional[str] = None
    pr_url: Optional[str] = None
    mutation_applied: bool = False
    analysis: Optional[Dict[str, Any]] = None
    results_file: Optional[str] = None
    summary_file: Optional[str] = None
    pr_results: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    traceback: Optional[str] = None

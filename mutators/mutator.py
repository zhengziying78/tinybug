"""
Utilities for applying configured mutations to repository checkouts.
"""
from __future__ import annotations

import re
from pathlib import Path
from typing import Any, Dict

from models.mutation import MutationSpec


class Mutator:
    """Applies regex-based mutations to files within a repository tree."""

    def __init__(self, repo_path: Path):
        self.repo_path = repo_path

    def apply_mutation(self, mutation_spec: MutationSpec) -> bool:
        """Apply the supplied mutation to the target file, returning True if changed."""
        target_file = self.repo_path / mutation_spec.file_path

        if not target_file.exists():
            raise FileNotFoundError(f"Target file not found: {target_file}")

        lines = target_file.read_text(encoding="utf-8").splitlines(keepends=True)

        if mutation_spec.line_number > len(lines) or mutation_spec.line_number < 1:
            raise IndexError(f"Line number {mutation_spec.line_number} is out of range")

        line_index = mutation_spec.line_number - 1
        original_line = lines[line_index]

        mutated_line = re.sub(
            mutation_spec.find_pattern,
            mutation_spec.replace_pattern,
            original_line,
        )

        if mutated_line == original_line:
            return False

        lines[line_index] = mutated_line
        target_file.write_text("".join(lines), encoding="utf-8")
        return True

    def create_mutation_from_dict(self, mutation_dict: Dict[str, Any]) -> MutationSpec:
        """Convenience helper that converts a config dictionary into a MutationSpec."""
        return MutationSpec(
            file_path=mutation_dict["file_path"],
            line_number=mutation_dict["line_number"],
            find_pattern=mutation_dict["find_pattern"],
            replace_pattern=mutation_dict["replace_pattern"],
        )

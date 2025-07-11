"""
Mutation application functionality for mutation testing PoC.
"""
import re
from pathlib import Path
from typing import Dict, Any


class MutationSpec:
    def __init__(self, file_path: str, line_number: int, find_pattern: str, replace_pattern: str):
        self.file_path = file_path
        self.line_number = line_number
        self.find_pattern = find_pattern
        self.replace_pattern = replace_pattern


class Mutator:
    def __init__(self, repo_path: Path):
        self.repo_path = repo_path
    
    def apply_mutation(self, mutation_spec: MutationSpec) -> bool:
        """Apply a mutation to the specified file."""
        target_file = self.repo_path / mutation_spec.file_path
        
        if not target_file.exists():
            raise FileNotFoundError(f"Target file not found: {target_file}")
        
        # Read the file
        with open(target_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        # Check if line number is valid
        if mutation_spec.line_number > len(lines) or mutation_spec.line_number < 1:
            raise IndexError(f"Line number {mutation_spec.line_number} is out of range")
        
        # Apply mutation to the specified line (1-indexed)
        line_index = mutation_spec.line_number - 1
        original_line = lines[line_index]
        
        # Apply regex replacement
        mutated_line = re.sub(mutation_spec.find_pattern, mutation_spec.replace_pattern, original_line)
        
        # Check if mutation was applied
        if mutated_line == original_line:
            return False  # No change made
        
        # Update the line
        lines[line_index] = mutated_line
        
        # Write back to file
        with open(target_file, 'w', encoding='utf-8') as f:
            f.writelines(lines)
        
        return True
    
    def create_mutation_from_dict(self, mutation_dict: Dict[str, Any]) -> MutationSpec:
        """Create a MutationSpec from a dictionary."""
        return MutationSpec(
            file_path=mutation_dict['file_path'],
            line_number=mutation_dict['line_number'],
            find_pattern=mutation_dict['find_pattern'],
            replace_pattern=mutation_dict['replace_pattern']
        )
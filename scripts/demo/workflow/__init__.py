"""
Console-demo workflow helpers.

Only the interactive ``run_single_mutation_flow`` entry point remains under the
``scripts.demo`` namespace; all production workflow code lives in ``temporal``.
"""

from scripts.demo.workflow.flow import run_single_mutation_flow

__all__ = ["run_single_mutation_flow"]

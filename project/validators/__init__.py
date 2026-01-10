"""
T3 Benchmark Validators Package.

This package provides validation tools for T3 benchmark cases.

Available validators:
- ContentValidator: Validates case content quality and completeness
- DAGValidator: Validates causal DAG structures (acyclicity, backdoor criterion, etc.)

DAG Validation Rules:
- DAG-01: Acyclicity Check (CRITICAL) - Ensures no cycles in causal graph
- DAG-02: Backdoor Criterion (HIGH) - Validates adjustment sets block backdoor paths
- DAG-03: Collider Conditioning (HIGH) - Warns about conditioning on colliders
- DAG-04: Variable Role Consistency (MEDIUM) - Checks roles match structure
"""

from .content_validator import (
    ContentValidationResult,
    ContentValidator,
    Dimension,
    Severity,
)

from .dag_validator import (
    DAGValidator,
    DirectedGraph,
    UndirectedGraph,
    ValidationResult,
    Severity as DAGSeverity,
)

__all__ = [
    # Content Validator
    "ContentValidationResult",
    "ContentValidator",
    "Dimension",
    "Severity",

    # DAG Validator
    "DAGValidator",
    "DirectedGraph",
    "UndirectedGraph",
    "ValidationResult",
    "DAGSeverity",
]
